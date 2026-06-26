from contextvars import ContextVar

client_ip_ctx: ContextVar[str] = ContextVar("client_ip", default=None)
