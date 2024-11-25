from fastapi import HTTPException, status


class ApiExceptionsError:
    @staticmethod
    def not_found_404(detail: str = 'Not found') -> HTTPException:
        return HTTPException(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def bad_request_400(detail: str = 'Bad Request') -> HTTPException:
        return HTTPException(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)
