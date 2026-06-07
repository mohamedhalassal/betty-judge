import asyncio
import html
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright
from sqlmodel import Session, select
import click
from sqlmodel import create_engine, Session, SQLModel

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))

TEST_SCHEMA_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST_SCHEMA_DIR))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
     raise click.ClickException("DATABASE_URL must be set in backend/.env")
engine = create_engine(DATABASE_URL)
from models.problem import Problem
from models.submission import Submission, SubmissionStatus
from models.user import User

# Configuration for the import process. Adjust these as needed.
GROUP_ID = "MEqF8b6wBT"
CONTEST_ID = "592431"
PAGE_NUMBER = 1
PROBLEM_FILTER = "V"
IMPORT_USER_ID = 1
IMPORT_PROBLEM_ID = 4
MAX_STATUS_PAGES = 50

BASE_URL = f"https://codeforces.com/group/{GROUP_ID}/contest/{CONTEST_ID}"
STATUS_URL = f"{BASE_URL}/status"
CDP_URL = "http://127.0.0.1:9222"

CHROME_PROFILE_DIR = Path("./real-chrome-codeforces-profile").resolve()


def normalize_source_code(source_code: str) -> str:
    return (
        source_code.replace("\ufeff", "")
        .replace("\u00a0", " ")
        .replace("\u2007", " ")
        .replace("\u202f", " ")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u200e", "")
        .replace("\u200f", "")
    )


def codeforces_verdict_to_submission_status(verdict: str) -> SubmissionStatus:
    normalized = verdict.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)

    if normalized.startswith("accepted"):
        return SubmissionStatus.ACCEPTED
    if normalized.startswith("wrong answer"):
        return SubmissionStatus.WRONG_ANSWER
    if normalized.startswith("time limit exceeded"):
        return SubmissionStatus.TIME_LIMIT_EXCEEDED
    if normalized.startswith("runtime error"):
        return SubmissionStatus.RUNTIME_ERROR
    if normalized.startswith("compilation error") or normalized.startswith("compile error"):
        return SubmissionStatus.COMPILE_ERROR
    if normalized.startswith("memory limit exceeded"):
        return SubmissionStatus.MEMORY_LIMIT_EXCEEDED
    if normalized.startswith("idleness limit exceeded"):
        return SubmissionStatus.IDLENESS_LIMIT_EXCEEDED
    return SubmissionStatus.IN_QUEUE


def parse_codeforces_time_ms(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"(\d+)", value.replace(",", ""))
    return int(match.group(1)) if match else None


def parse_codeforces_memory_bytes(value: str | None) -> int | None:
    if not value:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)\s*([kmgt]?b)?", value.strip(), re.IGNORECASE)
    if not match:
        return None

    amount = float(match.group(1))
    unit = (match.group(2) or "B").lower()
    multipliers = {
        "b": 1,
        "kb": 1024,
        "mb": 1024 * 1024,
        "gb": 1024 * 1024 * 1024,
        "tb": 1024 * 1024 * 1024 * 1024,
    }
    return int(amount * multipliers.get(unit, 1))


def parse_failed_test(verdict: str | None) -> int | None:
    if not verdict:
        return None
    match = re.search(r"\bon\s+test\s+(\d+)\b", verdict, re.IGNORECASE)
    return int(match.group(1)) if match else None


def required_int_env(name: str, value: str | None) -> int:
    if value is None or value == "":
        raise SystemExit(f"{name} must be set in backend/.env")
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"{name} must be an integer") from None


def import_problem_id() -> int:
    return IMPORT_PROBLEM_ID


def validate_import_targets(session: Session, problem_id: int) -> None:
    if session.get(Problem, problem_id) is None:
        raise SystemExit(f"Problem {problem_id} was not found in the database")
    if session.get(User, IMPORT_USER_ID) is None:
        raise SystemExit(f"User {IMPORT_USER_ID} was not found in the database")


def matches_problem_filter(submission: Dict[str, str]) -> bool:
    if not PROBLEM_FILTER:
        return True

    problem = re.sub(r"\s+", " ", submission["problem"].strip().lower())
    wanted = PROBLEM_FILTER.strip().lower()
    return (
        problem == wanted
        or problem.startswith(wanted + " ")
        or problem.startswith(wanted + " -")
        or problem.startswith(wanted + ".")
    )


def cdp_is_running() -> bool:
    try:
        with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=1) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def start_chrome() -> None:
    CHROME_PROFILE_DIR.mkdir(exist_ok=True)
    if cdp_is_running():
        return

    chrome = "/Applications/Google Chrome.app"
    subprocess.Popen(
        [
            "open",
            "-na",
            chrome,
            "--args",
            "--remote-debugging-port=9222",
            f"--user-data-dir={CHROME_PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            STATUS_URL,
        ]
    )

    for _ in range(30):
        if cdp_is_running():
            return
        time.sleep(1)

    raise SystemExit(
        "Could not start Chrome with remote debugging. Start it manually:\n"
        "open -na 'Google Chrome' --args --remote-debugging-port=9222 "
        f"--user-data-dir='{CHROME_PROFILE_DIR}'"
    )


async def wait_for_status_page(page) -> None:
    while True:
        try:
            await page.wait_for_selector("table.status-frame-datatable", timeout=30000)
            return
        except PlaywrightTimeoutError:
            body_text = await page.locator("body").inner_text(timeout=5000)
            if "You are not allowed to view the contest" in body_text:
                raise SystemExit(
                    "\nCodeforces says: You are not allowed to view the contest.\n"
                    "Log in with an account that is a member of this group and has "
                    "access to this contest, then run the script again."
                )

            click.echo("\nStill waiting for the status table.")
            click.echo(f"Current URL: {page.url}")
            click.echo("Use the opened Chrome window to log in / pass verification.")
            click.echo("Then navigate to:")
            click.echo(STATUS_URL)
        except PlaywrightError as error:
            if "Target page, context or browser has been closed" in str(error):
                raise SystemExit(
                    "\nChrome was closed. Run this script again and leave Chrome open "
                    "until it prints Done."
                )
            raise


async def get_page(browser):
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    for page in context.pages:
        if "codeforces.com" in page.url:
            return page
    return await context.new_page()


async def open_status_page(page) -> None:
    await page.goto(STATUS_URL, wait_until="domcontentloaded", timeout=120000)
    await wait_for_status_page(page)


async def last_status_page_number(page) -> int:
    labels = await page.locator(".pagination a, .pagination span").all_inner_texts()
    pages = [int(label.strip()) for label in labels if label.strip().isdigit()]
    return max(pages, default=1)


async def submissions_on_current_page(page) -> List[Dict[str, str]]:
    rows = await page.locator("table.status-frame-datatable tbody tr").all()
    submissions = []

    for row in rows:
        cells = [cell.strip() for cell in await row.locator("td").all_inner_texts()]
        if len(cells) < 6:
            continue

        submission_link = row.locator("a[href*='/submission/']").first
        if await submission_link.count() == 0:
            continue

        href = await submission_link.get_attribute("href", timeout=1000)
        match = re.search(r"/submission/(\d+)", href or "")
        if not match:
            continue

        submissions.append(
            {
                "id": match.group(1),
                "user": cells[1],
                "problem": cells[3],
                "language": cells[4],
                "verdict": cells[5],
                "time": cells[6] if len(cells) > 6 else "",
                "memory": cells[7] if len(cells) > 7 else "",
            }
        )

    return submissions


async def collect_submissions(page) -> List[Dict[str, str]]:
    await open_status_page(page)
    last_page = await last_status_page_number(page)
    pages_to_scan = min(last_page, MAX_STATUS_PAGES) if MAX_STATUS_PAGES else last_page
    click.echo(f"Detected {last_page} status page(s). Scanning {pages_to_scan}.")

    by_id: Dict[str, Dict[str, str]] = {}
    for status_page in range(1, pages_to_scan + 1):
        click.echo(f"Reading status page {status_page}/{pages_to_scan}")
        await page.goto(f"{STATUS_URL}/page/{status_page}", wait_until="domcontentloaded")
        await wait_for_status_page(page)
        for submission in await submissions_on_current_page(page):
            if not matches_problem_filter(submission):
                continue
            by_id[submission["id"]] = submission

    filtered_submissions = list(by_id.values())
    submissions = filtered_submissions
    if PAGE_NUMBER is not None:
        page_size = 50
        start = (PAGE_NUMBER - 1) * page_size
        end = start + page_size
        submissions = filtered_submissions[start:end]

    if PROBLEM_FILTER:
        click.echo(
            f"Found {len(filtered_submissions)} unique submission(s) for problem "
            f"{PROBLEM_FILTER!r} across all status pages."
        )
        if PAGE_NUMBER is not None:
            click.echo(
                f"Using filtered page {PAGE_NUMBER}: submissions "
                f"{start + 1}-{min(end, len(filtered_submissions))}."
            )
    else:
        click.echo(f"Found {len(filtered_submissions)} unique submission(s).")
    return submissions


async def read_submission_source(page, submission: Dict[str, str]) -> str | None:
    await page.goto(f"{BASE_URL}/submission/{submission['id']}", wait_until="domcontentloaded")
    try:
        await page.wait_for_selector("#program-source-text", timeout=60000)
    except PlaywrightTimeoutError:
        click.echo(f"Could not read source for submission {submission['id']}")
        return None

    source = await page.locator("#program-source-text").inner_text()
    return normalize_source_code(html.unescape(source))


def source_already_imported(
    session: Session,
    user_id: int,
    problem_id: int,
    source_code: str,
    codeforces_submission_id: int,
) -> bool:
    existing_submission = session.exec(
        select(Submission).where(
            Submission.user_id == user_id,
            Submission.problem_id == problem_id,
            Submission.codeforces_submission_id == codeforces_submission_id,
        )
    ).first()
    return existing_submission is not None


def store_submission(
    session: Session,
    submission: Dict[str, str],
    source_code: str,
    user_id: int,
    problem_id: int,
) -> bool:
    codeforces_submission_id = int(submission["id"])
    codeforces_verdict = codeforces_verdict_to_submission_status(submission["verdict"])
    if source_already_imported(
        session,
        user_id,
        problem_id,
        source_code,
        codeforces_submission_id,
    ):
        click.echo(f"Skipping existing source for Codeforces submission {submission['id']}")
        return False

    db_submission = Submission(
        user_id=user_id,
        problem_id=problem_id,
        source_code=source_code,
        codeforces_submission_id=codeforces_submission_id,
        codeforces_verdict=codeforces_verdict,
        codeforces_time_ms=parse_codeforces_time_ms(submission.get("time")),
        codeforces_memory_bytes=parse_codeforces_memory_bytes(submission.get("memory")),
        codeforces_failed_test=parse_failed_test(submission["verdict"]),
    )
    session.add(db_submission)
    session.commit()
    session.refresh(db_submission)
    click.echo(
        f"Inserted DB submission {db_submission.id} from Codeforces "
        f"{submission['id']} with verdict {codeforces_verdict.value}"
    )
    return True


async def main() -> None:
    start_chrome()
    problem_id = import_problem_id()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(CDP_URL)
        page = await get_page(browser)

        click.echo(f"Connected to Chrome on {CDP_URL}")
        click.echo(f"Chrome profile: {CHROME_PROFILE_DIR}")

        submissions = await collect_submissions(page)
        inserted_count = 0
        with Session(engine) as session:
            validate_import_targets(session, problem_id)
            for index, submission in enumerate(submissions, start=1):
                click.echo(f"Reading {index}/{len(submissions)}: {submission['id']}")
                source_code = await read_submission_source(page, submission)
                if source_code is None:
                    continue
                if store_submission(
                    session, submission, source_code, IMPORT_USER_ID, problem_id
                ):
                    inserted_count += 1

        await browser.close()
        click.echo(f"Done. Inserted {inserted_count} submission(s).")

@click.command()
@click.option("--problem-filter", default='V', help="Only import submissions for problems whose name starts with this string.")
@click.option("--page-number", type=int, default=None, help="Only import submissions from this status page number.")
@click.option("--user-id", type=int, default=1, help="The user ID to associate with the imported submissions.")
@click.option("--problem-id", type=int, default=4, help="The problem ID to associate with the imported submissions.")
@click.option("--max-status-pages", type=int, default=20, help="Maximum Codeforces status pages to scan before filtering.")
def import_submissions(problem_filter, page_number, user_id, problem_id, max_status_pages):
    global PROBLEM_FILTER, PAGE_NUMBER, IMPORT_USER_ID, IMPORT_PROBLEM_ID, MAX_STATUS_PAGES
    PROBLEM_FILTER = problem_filter
    PAGE_NUMBER = page_number
    IMPORT_USER_ID = user_id
    IMPORT_PROBLEM_ID = problem_id
    MAX_STATUS_PAGES = max_status_pages
    click.echo(
        f"Importing Codeforces submissions for problem filter {PROBLEM_FILTER!r} "
        f"into problem {IMPORT_PROBLEM_ID} as user {IMPORT_USER_ID}."
    )
    asyncio.run(main())

if __name__ == "__main__":
    import_submissions()
