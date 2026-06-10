import resource

def build_resource_limiter(cpu_limit_seconds: int, memory_limit_mb: int):
    # set limits for memory usage and stack size  
    max_memory = memory_limit_mb * 1024 * 1024 * 5
    stack_limit = 256 * 1024 * 1024

    def limit_resources():
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit_seconds, cpu_limit_seconds + 2))
            resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
            resource.setrlimit(resource.RLIMIT_STACK, (stack_limit, stack_limit))
        except (OSError, ValueError) as exc:
            raise RuntimeError("Sandbox resource limit setup failed") from exc

    return limit_resources