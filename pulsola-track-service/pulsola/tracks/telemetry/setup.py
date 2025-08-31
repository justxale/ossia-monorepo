from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def telemetry_setup(app: FastAPI) -> None:
    resource = Resource.create(attributes={SERVICE_NAME: 'pulsola-tracks'})

    exporter = OTLPSpanExporter(endpoint='http://tempo:4317', insecure=True)
    processor = BatchSpanProcessor(exporter)
    tracer_provider = TracerProvider(resource=resource)
    meter_provider = MeterProvider(resource=resource)

    TortoiseORMInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=tracer_provider, meter_provider=meter_provider
    )
    app.add_middleware(
        OpenTelemetryMiddleware,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
    )

    tracer_provider.add_span_processor(processor)

    trace.set_tracer_provider(tracer_provider)
    metrics.set_meter_provider(meter_provider)
