py dev/devtools/deletepycache.py
git add .
echo "Enter commit message: "
read commit_message
git commit -m "$commit_message"
git push origin main