from fastapi import HTTPException, status

async def get_current_user(current_user: dict):
    try:
        # Since 'protect' already fetched and verified the session data,
        # we can return it directly to the client.
        return current_user
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"get current user error: {str(error)}"
        )