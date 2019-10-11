from app import db
from app.auth.models import Role

role = Role(name="Company Admin", description="Administrator of a company. \
                                              Users with this role can modify \
                                              company data.")
db.session.add(role)
db.session.commit()

role = Role(name="Underwriter", description="Users with the ability to \
                                            evaluate deals.")
db.session.add(role)
db.session.commit()
