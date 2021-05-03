from services.misc import DefaultResponse

DETAIL_RESPONSES = {
    400:
        {
            "model": DefaultResponse,
        },
    404: {
        "model": DefaultResponse,
    }
}