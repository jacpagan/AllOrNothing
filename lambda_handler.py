from mangum import Mangum

from vague_language_detector.main import app

# Reuse the adapter across invocations to benefit from Lambda container reuse.
handler = Mangum(app)

