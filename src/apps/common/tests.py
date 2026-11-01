from django.test import TestCase


class HealthCheckTest(TestCase):
    """헬스체크 엔드포인트 테스트"""

    def test_성공__헬스체크_응답(self):
        """GET /api/health/ 요청 시 200과 상태 값을 반환"""
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
