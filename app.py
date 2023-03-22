import dash
from dash_extensions.enrich import MultiplexerTransform, DashProxy
import orjson

# meta_tags are required for the app layout to be mobile responsive
app = DashProxy(
    __name__,
    title="Insurance Finance Details",
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    transforms = [MultiplexerTransform()]
)
server = app.server
