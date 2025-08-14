from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from webapp import db
from webapp.models import Domain, Record
from webapp.auth import admin_required
from . import main
from .forms import DomainForm, RecordForm

@main.route('/')
@login_required
def index():
    domains = Domain.query.all()
    return render_template('index.html', domains=domains)

@main.route('/domain/<int:domain_id>')
@login_required
def domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    records = Record.query.filter_by(domain_id=domain_id).order_by(Record.type, Record.name).all()
    return render_template('domain.html', domain=domain, records=records)

@main.route('/domain/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_domain():
    form = DomainForm()
    if form.validate_on_submit():
        domain = Domain(name=form.name.data, description=form.description.data)
        db.session.add(domain)
        
        # Add default SOA record
        soa_record = Record(
            domain_id=domain.id,
            name='@',
            type='SOA',
            content=f'ns1.{domain.name} admin.{domain.name} 1 3600 1800 604800 86400',
            ttl=3600
        )
        db.session.add(soa_record)
        
        # Add default NS record
        ns_record = Record(
            domain_id=domain.id,
            name='@',
            type='NS',
            content=f'ns1.{domain.name}',
            ttl=3600
        )
        db.session.add(ns_record)
        
        db.session.commit()
        flash('Domain added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_domain.html', form=form)

@main.route('/record/add/<int:domain_id>', methods=['GET', 'POST'])
@login_required
def add_record(domain_id):
    form = RecordForm()
    domain = Domain.query.get_or_404(domain_id)
    
    if form.validate_on_submit():
        record = Record(
            domain_id=domain_id,
            name=form.name.data,
            type=form.type.data,
            content=form.content.data,
            ttl=form.ttl.data,
            priority=form.priority.data if form.type.data == 'MX' else None
        )
        db.session.add(record)
        db.session.commit()
        flash('Record added successfully!', 'success')
        return redirect(url_for('main.domain', domain_id=domain_id))
    
    return render_template('add_record.html', form=form, domain=domain)

@main.route('/record/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)
    form = RecordForm(obj=record)
    
    if form.validate_on_submit():
        record.name = form.name.data
        record.type = form.type.data
        record.content = form.content.data
        record.ttl = form.ttl.data
        record.priority = form.priority.data if form.type.data == 'MX' else None
        db.session.commit()
        flash('Record updated successfully!', 'success')
        return redirect(url_for('main.domain', domain_id=record.domain_id))
    
    return render_template('edit_record.html', form=form, record=record)

@main.route('/record/delete/<int:record_id>')
@login_required
@admin_required
def delete_record(record_id):
    record = Record.query.get_or_404(record_id)
    domain_id = record.domain_id
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('main.domain', domain_id=domain_id))

@main.route('/domain/delete/<int:domain_id>')
@login_required
@admin_required
def delete_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    db.session.delete(domain)
    db.session.commit()
    flash('Domain deleted successfully!', 'success')
    return redirect(url_for('main.index'))