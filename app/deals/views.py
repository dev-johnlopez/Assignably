from flask import Blueprint, g, render_template, redirect, url_for, g, flash, \
    request
from flask_security import current_user, current_user #, login_required
from app import db
from app.decorators import tenant_required, login_required
from app.email import send_email
from app.deals.forms import DealForm
from app.auth.models import User, Tenant
from app.deals.models import Deal, DealContact, DealContactRole, Contact, File
import os
import json
import boto3
import datetime
from werkzeug.utils import secure_filename
from botocore.client import Config

bp = Blueprint('deals', __name__)

#@bp.context_processor
#def inject_subdomain():
#    return dict(subdomain=current_user.tenant.subdomain)


@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@tenant_required
@login_required
def index(subdomain):
    #deals = current_user.get_deals()
    return render_template('deals/index.html',
                           title='Active Deals',
                           deals=[])


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create(subdomain):
    form = DealForm()
    if form.validate_on_submit():
        deal = Deal()
        for contact_form in form.contacts:
            deal_contact = DealContact()
            deal_contact.contact = current_user.contact
            role = DealContactRole(name="Created By")
            deal_contact.add_role(role)
            deal.add_contact(deal_contact)
        for file in form.files:
            file = File(url=file.url)
            deal.add_file(file)
        form.populate_obj(deal)
        current_user.tenant.add_deal(deal)
        db.session.add(current_user.tenant)
        db.session.add(deal)
        db.session.commit()
        return redirect(url_for('.view',
                                subdomain=subdomain, deal_id=deal.id))
    deal_contact_data = {
        'contact': current_user.contact,
        'roles': [DealContactRole(name="Created By")]
    }
    form.contacts.append_entry(deal_contact_data)
    return render_template('deals/new.html',
                           title="Create Deal",
                           form=form,
                           subdomain=subdomain)


@bp.route('/<tenant_id>/new', methods=['GET', 'POST'])
def iframe(subdomain, tenant_id):
    form = DealForm()
    if form.validate_on_submit():
        tenant = Tenant.query.get_or_404(tenant_id)
        deal = Deal()
        submitted_by = None
        for contact_form in form.contacts:
            deal_contact = DealContact()
            contact = Contact(first_name=contact_form.contact.first_name.data,
                              last_name=contact_form.contact.last_name.data,
                              phone=contact_form.contact.phone.data,
                              email=contact_form.contact.email.data)
            submitted_by = contact
            deal_contact.contact = contact
            role = DealContactRole(name="Created By")
            deal_contact.add_role(role)
            deal.add_contact(deal_contact)
        for file_form in form.files:
            file = File()
            file.url = file_form.url
            # file.file_type = 0
            deal.add_file(file)

        form.populate_obj(deal)
        deal_contact = DealContact()
        tenant.add_deal(deal)
        db.session.add(deal)
        db.session.add(tenant)
        db.session.commit()
        recipient = tenant.users[0].email
        if tenant.get_settings().partnership_email_recipient is not None:
            recipient = tenant.get_settings().partnership_email_recipient
        send_email('New Deal Notification!',
                   sender='support@assignably.com', recipients=[recipient],
                   text_body=render_template('emails/new_deal.txt',
                                             tenant=tenant,
                                             submitted_by=submitted_by,
                                             deal=deal),
                   html_body=render_template('emails/new_deal.html',
                                             tenant=tenant,
                                             submitted_by=submitted_by,
                                             deal=deal),
                   attachments=[],
                   sync=True)
        return render_template('deals/submitted.html',
                               user_id=user_id,
                               subdomain=subdomain)

    if len(form.contacts) == 0:
        deal_contact_data = {
            'contact': {},
            'roles': []
        }
        form.contacts.append_entry(deal_contact_data)
    return render_template('deals/iframe.html',
                           form=form,
                           subdomain=subdomain)


@bp.route('/<deal_id>/view')
@login_required
def view(subdomain, deal_id):
    deal = Deal.query.get_or_404(deal_id)
    return render_template('deals/view.html',
                           title="{}".format(deal),
                           deal=deal,
                           subdomain=subdomain)


@bp.route('/<deal_id>/delete')
@login_required
def delete(subdomain, deal_id):
    deal = Deal.query.get_or_404(deal_id)
    db.session.delete(deal)
    db.session.commit()
    return redirect(url_for('deals.index',
                            subdomain=subdomain))


@bp.route('/<deal_id>/photos')
@login_required
def add_photos(subdomain, deal_id):
    deal = Deal.query.get_or_404(deal_id)
    return render_template('deals/dropzone.html',
                           title="Upload Photos",
                           deal=deal,
                           subdomain=subdomain)


@bp.route('/<deal_id>/uploads', methods=['GET', 'POST'])
@login_required
def uploads(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join('/Users/johnlopez/Documents', f.filename))

    return 'upload template'


@bp.route('/<deal_id>/upload', methods=['GET', 'POST'])
@login_required
def upload(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    if request.method == 'POST':
        print(request.files)
        print(len(request.files))
        for x in range(0, len(request.files)):
            files = request.files.getlist('file[{}]'.format(x))
            for f in files:
                now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
                filename = now + '_' + str(current_user.id) + '_' + f.filename
                filename = secure_filename(filename)
                f.save(os.path.join('/Users/johnlopez/Documents', filename))
                print("saved!!!")

    return 'upload template'


@bp.app_template_filter()
def currency(value):
    if value is None:
        return "N/a"
    elif isinstance(value, int):
        return '${:,.2f}'.format(value)
    return value


@bp.route('/sign_s3/')
def sign_s3():
    S3_BUCKET = os.environ.get('S3_BUCKET')
    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')
    presigned_post = get_signed_s3_post(S3_BUCKET,
                                        file_name,
                                        file_type)
    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })


def get_signed_s3_post(bucket, file_name, file_type):
    s3 = \
        boto3.client('s3',
                     aws_access_key_id=os.environ.get('S3_KEY'),
                     aws_secret_access_key=os.environ.get(
                        'S3_SECRET_ACCESS_KEY'
                     ),
                     config=Config(signature_version='s3v4'),
                     region_name='us-east-2')

    presigned_post = s3.generate_presigned_post(
        Bucket=bucket,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type}
            ],
        ExpiresIn=3600
    )

    return presigned_post
