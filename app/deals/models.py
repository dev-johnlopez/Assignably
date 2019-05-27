from flask import current_app, url_for, g
from app import db, geolocator
from sqlalchemy import event

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    line_1 = db.Column(db.String(255))
    line_2 = db.Column(db.String(255))
    line_3 = db.Column(db.String(255))
    line_4 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state_code = db.Column(db.String(2))
    postal_code = db.Column(db.String(20))
    county = db.Column(db.String(255))
    country = db.Column(db.String(255))
    latitude = db.Column(db.Numeric(precision=9,scale=6))
    longitude = db.Column(db.Numeric(precision=9,scale=6))

    def __init__(self, **kwargs):
        super(Address, self).__init__(**kwargs)

    def __repr__(self):
        return '{}, {}, {} {}'.format(self.line_1, self.city, self.state_code, self.postal_code)

    def to_dict(self):
        data = {
            'id': self.id,
            'line_1': self.line_1,
            'line_2': self.line_2,
            'line_3': self.line_3,
            'line_4': self.line_4,
            'city': self.city,
            'state_code': self.state_code,
            'postal_code': self.postal_code,
            'county': self.county,
            'country': self.country
        }
        return data

    def from_dict(self, data):
        for field in data['line_1', 'line_2', 'line_3', 'line_4', 'city',
                            'state_code', 'postal_code', 'county', 'country']:
            if field in data:
                setattr(self, field, data[field])

    def geocode(self, **kwargs):
        line_1 = kwargs.get("line_1",self.line_1)
        city = kwargs.get("city",self.city)
        state_code = kwargs.get("state_code",self.state_code)
        postal_code = kwargs.get("postal_code",self.postal_code)
        self.latitude = None
        self.longitude = None
        try:
            location = geolocator.geocode('{} {} {} {}'.format(line_1, city, state_code, postal_code))
            if location is not None:
                self.latitude = location.latitude
                self.longitude = location.longitude
        except:
            current_app.logger.error('Unable to geocode address')

class Deal(db.Model):
    __tablename__ = 'deal'
    id = db.Column(db.Integer, primary_key=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)
    property_tax = db.Column(db.Integer)
    sq_feet = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    after_repair_value = db.Column(db.Integer)
    rehab_estimate = db.Column(db.Integer)
    purchase_price = db.Column(db.Integer)
    list_price = db.Column(db.Integer)
    under_contract_ind = db.Column(db.Boolean)
    contacts = db.relationship("DealContact")

    def add_contact(self, contact):
        if self.contacts is None:
            self.contacts = []
        self.contacts.append(contact)

    def get_submitter(self):
        return [deal_contact for deal_contact in self.contacts if deal_contact.is_submitter()][0]

    def to_dict(self):
        data = {
            'id': self.id,
            'address': self.address.to_dict(),
            'property_tax': self.property_tax,
            'sq_feet': self.sq_feet,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'after_repair_value': self.after_repair_value,
            'rehab_estimate': self.rehab_estimate,
            'purchase_price': self.purchase_price,
            'list_price': self.list_price,
            'under_contract_ind': self.under_contract_ind,
            'contacts' : [contact.to_dict() for contact in self.contacts],
            '_links': {
                'self': url_for('api.get_deal', id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['address', 'property_tax', 'sq_feet', 'bedrooms',
                            'bathrooms', 'after_repair_value', 'rehab_estimate',
                            'purchase_price', 'list_price',
                            'under_contract_ind', 'submitted_by']:
            if field == 'address' and field in data:
                self.address = Address()
                for address_field in data['address']:
                    setattr(self.address, address_field, data[field][address_field])
            elif field == 'submitted_by' and field in data:
                contact = Contact()
                for contact_field in data[field]:
                    setattr(contact, contact_field, data[field][contact_field])
                deal_contact = DealContact()
                deal_contact_role = DealContactRole(name="Submitted By")
                deal_contact.add_role(deal_contact_role)
                deal_contact.contact = contact
                self.add_contact(deal_contact)
            elif field in data:
                setattr(self, field, data[field])
        deal_contact = DealContact()
        deal_contact_role = DealContactRole(name="Submitted To")
        deal_contact.add_role(deal_contact_role)
        deal_contact.contact = g.current_user.contact
        self.add_contact(deal_contact)


class DealContact(db.Model):
    __tablename__ = "deal_contact"
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'))
    deal = db.relationship("Deal", back_populates="contacts")
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    contact = db.relationship("Contact", back_populates="deal_contacts")
    roles = db.relationship("DealContactRole")

    def add_role(self, role):
        if self.roles is None:
            self.roles = []
        self.roles.append(role)

    def is_submitter(self):
        return len([role for role in self.roles if role.name == "Submitted By"])

    def __repr__(self):
        return str(self.contact)

    def to_dict(self):
        data = {
            'id': self.id,
            'contact': self.contact.to_dict(),
            'roles': [role.to_dict() for role in self.roles]
        }
        return data

class DealContactRole(db.Model):
    __tablename__ = "deal_contact_role"
    id = db.Column(db.Integer, primary_key=True)
    deal_contact_id = db.Column(db.Integer, db.ForeignKey('deal_contact.id'))
    name = db.Column(db.String(255))

    def __repr__(self):
        return self.name

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    deal_contacts = db.relationship("DealContact")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="contact")
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def to_dict(self):
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email
        }
        return data

    def __repr__(self):
        return "{} {}".format(self.first_name, self.last_name)

def update_geocoding(mapper, connection, target):
    target.geocode()

event.listen(Address, 'before_insert', update_geocoding)
event.listen(Address, 'before_update', update_geocoding)
