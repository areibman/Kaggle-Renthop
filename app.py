#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for
from flask_wtf import Form
from wtforms.fields import RadioField, StringField, SubmitField
import stats
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


class RentalForm(Form):
    address = StringField('Location Address')
    features = StringField('List of features separated by commas',)
    manager_id = StringField('Manager id (leave blank if uknown)')
    building_id = StringField('building id (leave blank if uknown)')
    photos = StringField('URLs to photos separated by commas')
    description = StringField('Description of listing')
    bathrooms = StringField('Number of bathrooms')
    bedrooms = StringField('Number of bedrooms')
    price = StringField('Price')
    created = datetime.date
    submit = SubmitField('Submit')




@app.route('/', methods=['GET','POST'])
def index():
    form = RentalForm()
    if form.validate_on_submit():
        classy = stats.predicter(form.address, form.features, form.manager_id, form.building_id, form.photos,form.description, form.bathrooms, form.bedrooms, form.price)
        return render_template('results.html', classifier = classy)
    return render_template('index.html', form = form)

@app.route('/result', methods=['GET', 'POST'])
def result(results):
    return render_template('results.html')

    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
