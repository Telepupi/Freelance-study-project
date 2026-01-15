from app import create_app

print("starting run.py")

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)


