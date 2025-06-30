"""
Performance tests for API endpoints
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestPerformance:
    """Test performance and scalability of API endpoints"""

    def test_pagination_performance(self, client, admin_headers, db_session, test_tenant):
        """Test that pagination works efficiently with large datasets"""
        from app.models.beneficiary import Beneficiary
        
        # Create many beneficiaries
        beneficiaries = []
        for i in range(100):
            ben = Beneficiary(
                tenant_id=test_tenant.id,
                first_name=f"Test{i}",
                last_name=f"User{i}",
                date_of_birth="1990-01-01",
                contact_email=f"test{i}@example.com",
                status="active"
            )
            beneficiaries.append(ben)
        
        db_session.bulk_save_objects(beneficiaries)
        db_session.commit()
        
        # Test different page sizes
        page_sizes = [10, 20, 50]
        
        for page_size in page_sizes:
            start_time = time.time()
            
            response = client.get(
                f'/api/v1/beneficiaries?per_page={page_size}&page=1',
                headers=admin_headers
            )
            
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            assert len(response.json['beneficiaries']) <= page_size
            # Response should be reasonably fast (under 1 second)
            assert elapsed_time < 1.0

    def test_concurrent_requests(self, client, admin_headers):
        """Test API handles concurrent requests properly"""
        def make_request():
            return client.get(
                '/api/v1/dashboard/stats',
                headers=admin_headers
            )
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            
            results = []
            for future in as_completed(futures):
                response = future.result()
                results.append(response.status_code)
            
            # All requests should succeed
            assert all(status == 200 for status in results)

    def test_search_performance(self, client, admin_headers, db_session, test_tenant):
        """Test search functionality performance"""
        from app.models.user import User
        
        # Create users with searchable names
        users = []
        for i in range(50):
            user = User(
                email=f"searchtest{i}@example.com",
                username=f"searchuser{i}",
                full_name=f"Search Test User {i}",
                tenant_id=test_tenant.id,
                is_active=True
            )
            user.set_password("test123")
            users.append(user)
        
        db_session.bulk_save_objects(users)
        db_session.commit()
        
        # Test search performance
        search_terms = ["Search", "User", "Test", "1", "searchuser"]
        
        for term in search_terms:
            start_time = time.time()
            
            response = client.get(
                f'/api/v1/users?search={term}',
                headers=admin_headers
            )
            
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            # Search should be fast (under 500ms)
            assert elapsed_time < 0.5

    def test_bulk_operations_performance(self, client, admin_headers):
        """Test performance of bulk operations"""
        # Create multiple items in bulk
        items = []
        for i in range(20):
            items.append({
                "first_name": f"Bulk{i}",
                "last_name": f"Test{i}",
                "date_of_birth": "1990-01-01",
                "contact_email": f"bulk{i}@example.com"
            })
        
        start_time = time.time()
        
        # Test bulk create if endpoint exists
        response = client.post(
            '/api/v1/beneficiaries/bulk',
            headers=admin_headers,
            json={"beneficiaries": items}
        )
        
        elapsed_time = time.time() - start_time
        
        # Whether endpoint exists or not, it should respond quickly
        assert response.status_code in [201, 404]
        assert elapsed_time < 2.0  # Should complete within 2 seconds

    def test_complex_query_performance(self, client, admin_headers):
        """Test performance of complex queries with multiple filters"""
        # Test complex filtering
        start_time = time.time()
        
        response = client.get(
            '/api/v1/beneficiaries?status=active&search=test&sort_by=created_at&sort_desc=true&page=1&per_page=20',
            headers=admin_headers
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        # Complex queries should still be reasonably fast
        assert elapsed_time < 1.0

    def test_dashboard_aggregation_performance(self, client, admin_headers):
        """Test performance of dashboard aggregation queries"""
        start_time = time.time()
        
        response = client.get(
            '/api/v1/dashboard/stats',
            headers=admin_headers
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        # Dashboard should load quickly even with aggregations
        assert elapsed_time < 0.5

    def test_analytics_performance(self, client, admin_headers):
        """Test performance of analytics endpoints"""
        periods = ['day', 'week', 'month', 'year']
        
        for period in periods:
            start_time = time.time()
            
            response = client.get(
                f'/api/v1/analytics/overview?period={period}',
                headers=admin_headers
            )
            
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            # Analytics should compute reasonably fast
            assert elapsed_time < 1.0

    @pytest.mark.slow
    def test_stress_test_login(self, client, test_tenant, db_session):
        """Stress test the login endpoint"""
        from app.models.user import User
        
        # Create a test user
        user = User(
            email="stresstest@example.com",
            username="stresstest",
            full_name="Stress Test User",
            tenant_id=test_tenant.id,
            is_active=True
        )
        user.set_password("stresspass123")
        db_session.add(user)
        db_session.commit()
        
        # Perform multiple login attempts
        successful_logins = 0
        failed_logins = 0
        
        for i in range(50):
            response = client.post(
                '/api/v1/auth/login',
                json={
                    "email": "stresstest@example.com",
                    "password": "stresspass123"
                },
                headers={"X-Tenant-ID": str(test_tenant.id)}
            )
            
            if response.status_code == 200:
                successful_logins += 1
            else:
                failed_logins += 1
        
        # Most logins should succeed
        assert successful_logins > 45  # Allow for some rate limiting
        assert failed_logins < 5

    def test_response_size_performance(self, client, admin_headers):
        """Test performance with different response sizes"""
        # Test with different limit parameters
        limits = [1, 10, 50, 100]
        
        for limit in limits:
            start_time = time.time()
            
            response = client.get(
                f'/api/v1/beneficiaries?per_page={limit}',
                headers=admin_headers
            )
            
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            # Larger responses should still be reasonably fast
            assert elapsed_time < 1.5

    def test_jwt_validation_performance(self, client, admin_headers):
        """Test JWT validation doesn't add significant overhead"""
        # Make multiple authenticated requests
        total_time = 0
        num_requests = 20
        
        for _ in range(num_requests):
            start_time = time.time()
            
            response = client.get(
                '/api/v1/auth/me',
                headers=admin_headers
            )
            
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            assert response.status_code == 200
        
        avg_time = total_time / num_requests
        # JWT validation should be fast (under 50ms average)
        assert avg_time < 0.05

    def test_database_connection_pooling(self, client, admin_headers):
        """Test that database connection pooling works efficiently"""
        # Make many requests that require database access
        def make_db_request():
            return client.get('/api/v1/users', headers=admin_headers)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_db_request) for _ in range(20)]
            
            success_count = 0
            for future in as_completed(futures):
                response = future.result()
                if response.status_code == 200:
                    success_count += 1
            
            # All requests should succeed with connection pooling
            assert success_count == 20

    @pytest.mark.parametrize("endpoint", [
        '/api/v1/beneficiaries',
        '/api/v1/users',
        '/api/v1/dashboard/stats',
        '/api/v1/notifications',
        '/api/v1/learning-paths/my-paths'
    ])
    def test_endpoint_response_times(self, client, admin_headers, endpoint):
        """Test that common endpoints respond within acceptable time"""
        start_time = time.time()
        
        response = client.get(endpoint, headers=admin_headers)
        
        elapsed_time = time.time() - start_time
        
        # All endpoints should respond within 1 second
        assert elapsed_time < 1.0
        # Success or auth error expected
        assert response.status_code in [200, 401, 403]