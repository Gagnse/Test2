import requests
import json


class SpaceLogicApiClient:
    """
    Client for testing the SpaceLogic REST API
    """

    def __init__(self, base_url="http://localhost:5000/api"):
        """
        Initialize the API client

        Args:
            base_url (str): Base URL for the API
        """
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, email, password):
        """Log in to the API"""
        url = f"{self.base_url}/auth/login"
        payload = {"email": email, "password": password}
        response = self.session.post(url, json=payload)
        return response.json()

    def signup(self, nom, prenom, email, password):
        """Sign up for an account"""
        url = f"{self.base_url}/auth/signup"
        payload = {
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "password": password
        }
        response = self.session.post(url, json=payload)
        return response.json()

    def logout(self):
        """Log out from the API"""
        url = f"{self.base_url}/auth/logout"
        response = self.session.post(url)
        return response.json()

    def auth_status(self):
        """Check authentication status"""
        url = f"{self.base_url}/auth/status"
        response = self.session.get(url)
        return response.json()

    def get_projects(self):
        """Get all projects for the authenticated user"""
        url = f"{self.base_url}/projects"
        response = self.session.get(url)
        return response.json()

    def create_project(self, project_number, name, description=None, status=None, type=None):
        """Create a new project"""
        url = f"{self.base_url}/projects"
        payload = {
            "project_number": project_number,
            "nom": name
        }

        if description:
            payload["description"] = description
        if status:
            payload["status"] = status
        if type:
            payload["type"] = type

        response = self.session.post(url, json=payload)
        return response.json()

    def get_project(self, project_id):
        """Get a specific project by ID"""
        url = f"{self.base_url}/projects/{project_id}"
        response = self.session.get(url)
        return response.json()

    def update_project(self, project_id, updates):
        """Update a specific project"""
        url = f"{self.base_url}/projects/{project_id}"
        response = self.session.put(url, json=updates)
        return response.json()

    def get_organisations(self):
        """Get all organisations for the authenticated user"""
        url = f"{self.base_url}/organisations"
        response = self.session.get(url)
        return response.json()


# Example usage
if __name__ == "__main__":
    client = SpaceLogicApiClient()

    # Login
    result = client.login("sgagnon@stgm.net", "password123")
    print("Login Result:", result)

    # Check auth status
    auth_status = client.auth_status()
    print("Auth Status:", auth_status)

    # Get projects
    if auth_status.get('authenticated', False):
        projects = client.get_projects()
        print("Projects:", json.dumps(projects, indent=2))

        # Create a new project
        new_project = client.create_project(
            project_number="API-TEST-001",
            name="Test Project from API",
            description="This project was created using the REST API"
        )
        print("New Project:", json.dumps(new_project, indent=2))

        # Get organisations
        organisations = client.get_organisations()
        print("Organisations:", json.dumps(organisations, indent=2))

    # Logout
    logout_result = client.logout()
    print("Logout Result:", logout_result)