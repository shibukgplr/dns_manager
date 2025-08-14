from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, IPAddress
from webapp.models import User, Domain

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class DomainForm(FlaskForm):
    name = StringField('Domain Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Domain')

    def validate_name(self, name):
        domain = Domain.query.filter_by(name=name.data).first()
        if domain is not None:
            raise ValidationError('Domain already exists.')

class RecordForm(FlaskForm):
    type = SelectField('Record Type', choices=[
        ('A', 'A (IPv4 Address)'),
        ('AAAA', 'AAAA (IPv6 Address)'),
        ('CNAME', 'CNAME (Canonical Name)'),
        ('MX', 'MX (Mail Exchange)'),
        ('TXT', 'TXT (Text)'),
        ('NS', 'NS (Name Server)'),
        ('SOA', 'SOA (Start of Authority)')
    ], validators=[DataRequired()])
    name = StringField('Name')
    content = StringField('Value', validators=[DataRequired()])
    ttl = IntegerField('TTL', default=3600, validators=[DataRequired()])
    priority = IntegerField('Priority (MX only)', default=10)
    submit = SubmitField('Save Record')

    def validate_content(self, content):
        if self.type.data == 'A':
            try:
                IPAddress(version=4)(self, content)
            except ValidationError:
                raise ValidationError('Invalid IPv4 address')
        elif self.type.data == 'AAAA':
            try:
                IPAddress(version=6)(self, content)
            except ValidationError:
                raise ValidationError('Invalid IPv6 address')