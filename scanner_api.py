from flask import Flask, request, jsonify
from supabase import create_client
import os
from datetime import datetime

# === Initialize Flask App ===
app = Flask(__name__)

# === Initialize Supabase ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/scan")
def scan_qr():
    project_id = request.args.get("project")
    frame_code = request.args.get("frame")
    done_flag = request.args.get("done")

    if not project_id or not frame_code or done_flag != "true":
        return "Invalid QR code parameters", 400

    frame_id = f"{project_id}-{frame_code}"
    now_utc = datetime.utcnow().isoformat()

    # === Update frame with progress + timestamp ===
    supabase.table("frames").update({
        "progress": "Done",
        "scanned_at": now_utc
    }).eq("frame_id", frame_id).execute()

    # === If all frames in the project are Done, mark project Completed ===
    response = supabase.table("frames").select("progress").eq("project_id", project_id).execute()
    progresses = [r["progress"] for r in response.data]
    if progresses and all(p == "Done" for p in progresses):
        supabase.table("projects").update({
            "status": "Completed"
        }).eq("project_id", project_id).execute()

    return f"✅ Frame {frame_code} marked as done at {now_utc}", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
