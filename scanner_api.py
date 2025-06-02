from flask import Flask, request
import requests
import os

app = Flask(__name__)

# CONFIG
SUPABASE_URL = "https://wobhphzjaxyoqooiqfcp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvYmhwaHpqYXh5b3Fvb2lxZmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4Njk2MzEsImV4cCI6MjA2NDQ0NTYzMX0.kkbG9fvJ9iFGjG6yTIUdVroFZZdBjHx9_IONE_MShtI"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.route("/scan")
def scan():
    project = request.args.get("project")
    frame = request.args.get("frame")
    step = request.args.get("step")

    if not project:
        return "❌ Missing project ID", 400

    if step:  # Step scan
        frame_id = f"{project}-{frame}"
        data = {"status": "Completed"}
        query = f"?frame_id=eq.{frame_id}&step_id=eq.{step}"

        res = requests.patch(
            f"{SUPABASE_URL}/rest/v1/framesteps{query}",
            headers=HEADERS,
            json=data
        )

        if not res.ok:
            return f"❌ Failed to update step: {res.text}", 500

        # Check if all steps are completed
        check = requests.get(
            f"{SUPABASE_URL}/rest/v1/framesteps?select=*&frame_id=eq.{frame_id}",
            headers=HEADERS
        )
        steps = check.json()
        if all(s["status"] == "Completed" for s in steps):
            update = requests.patch(
                f"{SUPABASE_URL}/rest/v1/projects?project_id=eq.{project}",
                headers=HEADERS,
                json={"status": "Completed"}
            )

        return f"✅ Step '{step}' for frame '{frame_id}' marked complete."

    else:  # Project QR scanned
        res = requests.patch(
            f"{SUPABASE_URL}/rest/v1/projects?project_id=eq.{project}",
            headers=HEADERS,
            json={"status": "In Progress"}
        )
        if res.ok:
            return f"✅ Project {project} marked as In Progress"
        else:
            return f"❌ Failed to update project: {res.text}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

