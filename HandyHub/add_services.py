from Handy import create_app, db
from Handy.models import Service

app = create_app()

# Explicitly push the app context
with app.app_context():
    services = ["Plumbing", "Electrician", "Carpentry", "Cleaning", "Painting",'Gardening']

    for service in services:
        if not Service.query.filter_by(name=service).first():  # Avoid duplicates
            new_service = Service(name=service)
            db.session.add(new_service)

    db.session.commit()
    print("Services added successfully!")
