"""Rebuild embeddings after sitemap crawl"""
import subprocess
import sys

print("🔄 Rebuilding embeddings from new data...")

# Step 1: Create embeddings
print("\n1️⃣ Creating embeddings...")
result = subprocess.run([sys.executable, "src/embeddings/create_embeddings.py"], 
                       capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(f"❌ Error: {result.stderr}")
    sys.exit(1)

# Step 2: Restart API (kill old process if running)
print("\n2️⃣ Restarting API server...")
print("Please manually restart the API:")
print("  1. Stop old API (Ctrl+C in the terminal)")
print("  2. Run: python src/api/main.py")

print("\n3️⃣ Restart Streamlit frontend:")
print("  Run: streamlit run app.py")

print("\n✅ Done! Your chatbot now has the full dataset from sitemap!")
