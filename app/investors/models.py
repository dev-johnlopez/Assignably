from app import db


class Investor(db.Model):
    __tablename__ = 'investor'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    tenant = db.relationship("Tenant", back_populates="investors")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")
    criteria = db.relationship("InvestmentCriteria")


class LocationCriteria(db.Model):
    __tablename__ = 'locationcriteria'
    id = db.Column(db.Integer, primary_key=True)
    location_type = db.Column(db.String(255))
    location_code = db.Column(db.String(2))
    criteria_id = db.Column(db.Integer, db.ForeignKey('investmentcriteria.id'))

    def doesDealMatchLocation(self, deal):
        if location_type == "State":
            return deal.state_code == location_code
        if location_type == "Zip Code":
            return deal.postal_code == location_code
        return False


class InvestmentCriteria(db.Model):
    __tablename__ = 'investmentcriteria'
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'))
    investor = db.relationship("Investor", back_populates="criteria")
    property_type = db.Column(db.Integer)
    flip = db.Column(db.Integer)
    rental = db.Column(db.Integer)
    minimum_units = db.Column(db.Integer)
    maximum_units = db.Column(db.Integer)
    locations = db.relationship('LocationCriteria')

    def getPropertyType(self):
        return 'Test'
          #return CONSTANTS.PROPERTY_TYPE[self.property_type]

    def getDetailedPropertyType(self):
        return "Test 2"
        #if self.property_type == CONSTANTS.SFR:
        #    return self.getPropertyType()
        #if self.maximum_units == -1:
        #    return '{} ({}+ Units)'.format(self.getPropertyType(), self.minimum_units)
        #else:
        #    return '{} ({}-{} Units)'.format(self.getPropertyType(), self.minimum_units, self.maximum_units)

    def getLocations(self):
        return ', '.join(location.location_code for location in self.locations)

    def doesDealMatchCriteria(self, deal):
        num_units = deal.units
        if self.minimum_units > self.num_units:
            return False
        if self.maximum_units < num_units and self.maximum_units > 0:
            return False
        for location in self.locations:
            if location.doesDealMatchLocation(self, deal):
                return True
        return False
