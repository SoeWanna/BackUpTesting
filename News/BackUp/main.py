# -*- coding: utf-8 -*
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import json
import os
import logging
import pytz
import requests
import werkzeug.utils
import werkzeug.wrappers

from itertools import islice
from xml.etree import ElementTree as ET

import odoo
import jwt
import pathlib
import ast

#from datetime import datetime
from odoo import http, models, fields, _
from odoo.http import request, Response
from odoo.tools import OrderedSet
from odoo.addons.http_routing.models.ir_http import slug, _guess_mimetype
from odoo.addons.web.controllers.main import Binary
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.web import Home
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from random import randint
from passlib.context import CryptContext
from operator import itemgetter

logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)

class ClassWithGlobalEmailFunction:
    global send_email
    def send_email(useremail,message,subject):
        emailheaders = {'content-type': 'application/json'}
        email = useremail
        msg = message
        sub = subject
        emaildatas = {
                    "phone":email,
                    "text": sub,
                    "maillist":[],
                    "text2":msg,
                    "type":4,
                    }
        #emailurl = "https://connect.mitcloud.com/apx/module001/serviceEmail/sentEmail"
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','email')])
        emailurl = dynamic_url.x_name
        #emailurl = "http://connect.nirvasoft.com/apx/module001/serviceEmail/sentEmail"
        emailresponse = requests.post(emailurl, data=json.dumps(emaildatas), headers=emailheaders)
        y = emailresponse.json()
        return y


class Qualification(http.Controller):
    @http.route('/peproexperience/', website=True, auth='public', method='POST')
    def qualifications_function(self, **kw):
        name = kw.get('name')
        peid = kw.get('id')
        if not name:
            name = 1
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        return http.request.render('website.peproexperienceforms',{'sresult':name,'peid':peid})
   
   

    @http.route('/peinvolvement/', website=True, auth='public', method='POST')
    def qualifications_function1(self, **kw):
        name = kw.get('name')
        if not name:
            name = ''
        return http.request.render('website.peinvolvement',{'sresult':name})

    @http.route('/pesummary/', website=True, auth='public', method='POST')
    def qualifications_function2(self, **kw):
        name = kw.get('name')
        if not name:
            name = ''
        return http.request.render('website.pesummary',{'sresult':name})

    @http.route('/peverify/', website=True, auth='public', method='POST')
    def qualifications_function3(self, **kw):
        name = kw.get('name')
        if not name:
            name = ''
        return http.request.render('website.peverify',{'sresult':name})

    @http.route('/peproexperience1', website=True, auth='public', method='POST')
    def qualifications_function1(self, **kw):
        name = kw.get('name')
        peid = kw.get('id')
        if not name:
            name = 1
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        return http.request.render('website.peinvolvement',{'sresult':name,'peid':peid})
   

    @http.route(['/peproexperience2'], type='http', auth='public', website=True)
    def summary(self, **kw):
        name = kw.get('name')
        peid = kw.get('id')
        if not name:
            name = 1
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        return http.request.render('website.pesummary', {'sresult':name,'peid':peid})


    @http.route('/peproexperience3/', website=True, auth='public', method='POST')
    def qualifications_function3(self, **kw):
        name = kw.get('name')
        peid = kw.get('id')
        if not name:
            name = 1
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        return http.request.render('website.peverify',{'sresult':name,'peid':peid})



    @http.route('/save_peproexperience/', type='http', auth="public", methods=['POST'], website=True)
    def job_confirm(self, **post):
        x_proexperience_a1 = post.get('1-x_proexperience_a1')
        x_proexperience_a2 = post.get('1-x_proexperience_a2')
        x_name = post.get('1-x_name')
        x_proexperience_c = post.get('1-x_proexperience_c')
        x_proexperience_d1_total = post.get('1-x_proexperience_d1_total')
        x_proexperience_d2_total = post.get('1-x_proexperience_d2_total')
        x_proexperience_d3_total = post.get('1-x_proexperience_d3_total')
        x_proexperience_d4_total = post.get('1-x_proexperience_d4_total')
        x_proexperience_d5_total = post.get('1-x_proexperience_d5_total')
        x_proexperience_e = post.get('1-x_proexperience_e')
        if x_proexperience_a1 or x_proexperience_a2 or x_name or x_proexperience_c or x_proexperience_d1_total or x_proexperience_d2_total or x_proexperience_d2_total or x_proexperience_d3_total or x_proexperience_d4_total or x_proexperience_d5_total or x_proexperience_e:
           job_datas = self._process_job_details(post)
           Job = request.env['x_proexperience']
           for job_data in job_datas:
               Job += Job.sudo().create(job_data)
        pe = post.get('1-x_applicant')
        peid = int(pe)
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        pedata = http.request.env['x_involve'].sudo().search([('x_applicant','=',peid)])
        return http.request.render('website.peinvolvement',{'sresult':1,'peid':peid,'pedata':pedata})
        #return request.redirect('/peproexperience1')

    def _process_job_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route('/submit_peproexperience/', type='http', auth="public", methods=['POST'], website=True)
    def job_confirm1(self, **post):
       job_datas = self._process_job_details(post)
       pe = post.get('1-x_applicant')
       peid = int(pe)
       #pe = request.website._website_form_last_record().sudo().id
       Job = request.env['x_proexperience'].sudo().search([('x_applicant','=',peid)])
       #for job in Job:
           #for job_data in job_datas:
               #test = request.env['x_proexperience'].sudo().search([('id','=',job_data['id'])])
               #Job = test.sudo().write(job_data)
       if Job:
          pedatas = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',peid)]).unlink()
          if pedatas:
             PE = request.env['x_proexperience']
             for verify_data in job_datas:
                 PE += PE.sudo().create(verify_data)
       pedata = http.request.env['x_involve'].sudo().search([('x_applicant','=',peid)])
       pecount = http.request.env['x_involve'].sudo().search_count([('x_applicant','=',peid)])
       name = 1
       return http.request.render('website.peinvolvement',{'pedata':pedata, 'sresult':name,'peid':peid,'pecount':pecount})
#       return request.redirect('/peproexperience1')

    @http.route('/review_rfpe_renewal', website=True, auth='public', method='POST')
    def review_rfpe_renewal(self, **kw):
        par_id = request.env.user.partner_id.id
        peid = kw.get('id')
        rsecdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        ddata = http.request.env['x_discipline'].sudo().search([])
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        return http.request.render('website.review-rfpe-renewal',{'renewal_data':rsecdata, 'todaydate':todaydate,'fdate':fdate,'edate':edate,'nrc':nrc, 'nrcmm':nrcmm, 'paydata':paydata,'academicfiles': academicfiles, 'identityfiles': identityfiles})

    @http.route('/review_rlpe_renewal', website=True, auth='public', method='POST')
    def review_rlpe_renewal(self, **kw):
        par_id = request.env.user.partner_id.id
        peid = kw.get('id')
        rsecdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        ddata = http.request.env['x_discipline'].sudo().search([])
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        return http.request.render('website.review-rlpe-renewal',{'renewal_data':rsecdata, 'todaydate':todaydate,'fdate':fdate,'edate':edate,'nrc':nrc, 'nrcmm':nrcmm, 'paydata':paydata,'academicfiles': academicfiles, 'identityfiles': identityfiles})

    @http.route('/review_rec_renewal', website=True, auth='public', method='POST')
    def review_rec_renewal(self, **kw):
        par_id = request.env.user.partner_id.id
        peid = kw.get('id')
        rsecdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        ddata = http.request.env['x_discipline'].sudo().search([])
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        return http.request.render('website.review-rec-renewal',{'renewal_data':rsecdata, 'todaydate':todaydate,'fdate':fdate,'edate':edate,'nrc':nrc, 'nrcmm':nrcmm, 'paydata':paydata,'academicfiles': academicfiles, 'identityfiles': identityfiles})

    @http.route('/review_rle_renewal', website=True, auth='public', method='POST')
    def review_rle_renewal(self, **kw):
        par_id = request.env.user.partner_id.id
        peid = kw.get('id')
        rledata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        ddata = http.request.env['x_discipline'].sudo().search([])
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        return http.request.render('website.review-rle-renewal',{'renewal_data':rledata, 'todaydate':todaydate,'fdate':fdate,'edate':edate,'nrc':nrc, 'nrcmm':nrcmm, 'paydata':paydata,'academicfiles': academicfiles, 'identityfiles': identityfiles})



    @http.route('/review_rsec_renewal', website=True, auth='public', method='POST')
    def review_rsec_renewal(self, **kw):
        par_id = request.env.user.partner_id.id
        peid = kw.get('id')
        rsecdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        ddata = http.request.env['x_discipline'].sudo().search([])
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        return http.request.render('website.review-rsec-renewal',{'renewal_data':rsecdata, 'todaydate':todaydate,'fdate':fdate,'edate':edate,'nrc':nrc, 'nrcmm':nrcmm,'sample':sample, 'paydata':paydata,'academicfiles': academicfiles, 'identityfiles': identityfiles})


    @http.route('/review_renewal', website=True, auth='public', method='POST')
    def review_renewal(self, **kw):
        par_id = request.env.user.partner_id.id
        peid = kw.get('id')
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        ddata = http.request.env['x_discipline'].sudo().search([])
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        return http.request.render('website.review-renew',{'renewal_data':pedata, 'todaydate':todaydate,'fdate':fdate,'edate':edate,'nrc':nrc, 'nrcmm':nrcmm,'sample':sample, 'paydata':paydata,'academicfiles': academicfiles, 'identityfiles': identityfiles})

    @http.route('/review_pe', website=True, auth='public', method='POST')
    def back_pe(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        #peid = request.website._website_form_last_record().sudo().id
        peid = kw.get('id')
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        #pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        township = http.request.env['x_township'].sudo().search([])
        state = http.request.env['x_state'].sudo().search([])
        #resid = kw.get('id')
        careerfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_career')])
        programfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_program')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        firstdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_firstdegree_attachment')])
        postdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_postdegree_attachment')])
        return http.request.render('website.previous-pe-registration',{'state':state,'township':township,'pedata':pedata,'sresult':name,'nrc':nrc,'nrcmm':nrcmm,'careerfiles':careerfiles,'programfiles':programfiles,'academicfiles':academicfiles,'firstdegreefiles':firstdegreefiles,'postdegreefiles':postdegreefiles,'ddata':ddata})

    @http.route('/previousperegistration1',type='http', website=True, auth='public', method=['POST'])
    def back_pe1(self, **post):
        name = post.get('name')
        if not name:
            name = 1
        pe = post.get('1-x_applicant')
        peid = int(pe)
        #peid = request.website._website_form_last_record().sudo().id
        ddata = http.request.env['x_discipline'].sudo().search([])
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        township = http.request.env['x_township'].sudo().search([])
        state = http.request.env['x_state'].sudo().search([])
        careerfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_career')])
        programfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_program')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        firstdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_firstdegree_attachment')])
        postdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_postdegree_attachment')])
        if post and request.httprequest.method == 'POST':
           job_datas = self._process_job(post)
           pid = int(peid)
           Job = request.env['x_proexperience'].sudo().search([('x_applicant','=',pid)])
           x_proexperience_a1 = post.get('1-x_proexperience_a1')
           x_proexperience_a2 = post.get('1-x_proexperience_a2')
           x_name = post.get('1-x_name')
           x_proexperience_c = post.get('1-x_proexperience_c')
           x_proexperience_d1_total = post.get('1-x_proexperience_d1_total')
           x_proexperience_d2_total = post.get('1-x_proexperience_d2_total')
           x_proexperience_d3_total = post.get('1-x_proexperience_d3_total')
           x_proexperience_d4_total = post.get('1-x_proexperience_d4_total')
           x_proexperience_d5_total = post.get('1-x_proexperience_d5_total')
           x_proexperience_e = post.get('1-x_proexperience_e')
           if x_proexperience_a1 or x_proexperience_a2 or x_name or x_proexperience_c or x_proexperience_d1_total or x_proexperience_d2_total or x_proexperience_d3_total or x_proexperience_d4_total or x_proexperience_d5_total or x_proexperience_e:
              if not Job:
                 jb_datas = self._process_job(post)
                 Jb = request.env['x_proexperience']
                 for jb_data in jb_datas:
                     Jb += Jb.sudo().create(jb_data)
           #if Job:
              #for job in Job:
                  #for job_data in job_datas:
                      #test = request.env['x_proexperience'].sudo().search([('id','=',job_data['id'])])
                      #Job = test.sudo().write(job_data)
           if Job:
              pedatas = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',pid)]).unlink()
              if pedatas:
                 PE = request.env['x_proexperience']
                 for verify_data in job_datas:
                     PE += PE.sudo().create(verify_data)
        return http.request.render('website.peregistrationform',{'township':township,'state':state,'academicfiles':academicfiles,'firstdegreefiles':firstdegreefiles,'postdegreefiles':postdegreefiles,'pdata':pedata,'ddata':ddata,'sresult':name,'nrc':nrc,'nrcmm':nrcmm,'careerfiles':careerfiles,'programfiles':programfiles,'ddata':ddata})
       # return http.request.render('website.previous-pe-registration',{'academicfiles':academicfiles,'firstdegreefiles':firstdegreefiles,'postdegreefiles': postdegreefiles,'pdata':pedata,'ddata':ddata,'sresult':name,'nrc':nrc,'nrcmm':nrcmm,'careerfiles':careerfiles,'programfiles':programfiles})

    def _process_job(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())


    @http.route('/previouspeproexperience2', type='http', auth='public', website=True)
    def pe_back_test(self, **kw):
         name = kw.get('name')
         if not name:
             name = 1
        # peid = kw.get('id')
         peid = request.website._website_form_last_record().sudo().id
         pedata = http.request.env['x_summary'].sudo().search([('x_applicant','=',peid)])
         pecount = http.request.env['x_summary'].sudo().search_count([('x_applicant','=',peid)])
         return http.request.render('website.pesummary', {'pedata': pedata,'sresult':name,'pecount':pecount})



    @http.route('/submit_verify/', type='http', auth="public", methods=['POST'], website=True)
    def verify_back_submit(self, **post):
        #verify_datas = self._process_verify_details(post)
        id = post.get('1-x_applicant')
        peid = int(id)
        Job = request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
        update_infos = request.env['hr.applicant'].sudo().search([('id','=',peid)])
        jid = update_infos.job_id.id
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'4', 'x_applicant_id': peid, 'x_job_id': jid }
        history.sudo().create(hvalue)
        partner_name = update_infos.partner_name
        x_nrc4en = update_infos.x_nrc4en
        x_dob = update_infos.x_dob
        x_nrc_photo_front = update_infos.x_nrc_photo_front
        x_nrc_photo_back = update_infos.x_nrc_photo_back
        x_address_en = update_infos.x_address_en
        x_per_address_en = update_infos.x_per_address_en
        partner_phone = update_infos.partner_phone
        x_per_tel_no = update_infos.x_per_tel_no
        email_from = update_infos.email_from
        #x_per_email = update_infos.x_per_email
        x_per_email = request.env.user.login
        x_firstdegree_uni = update_infos.x_firstdegree_uni
        x_firstdegree_graduation_year = update_infos.x_firstdegree_graduation_year
        x_firstdegree_engineer_discipline = update_infos.x_firstdegree_engineer_discipline
        x_discipline_s = update_infos.x_discipline
        firstdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_firstdegree_attachment')])
        pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
        #if not partner_name and x_nrc4en and x_dob and x_nrc_photo_front and x_nrc_photo_back and x_address_en and x_per_address_en and partner_phone and x_per_tel_no and email_from and x_per_email and x_firstdegree_uni and x_firstdegree_graduation_year and x_firstdegree_engineer_discipline and x_discipline_s and firstdegreefiles: 
        if not partner_name or not x_nrc4en or not x_dob or not x_nrc_photo_front or not x_nrc_photo_back or not x_address_en or not x_per_address_en or not partner_phone or not x_per_tel_no or not email_from or not x_per_email or not x_firstdegree_uni or not x_firstdegree_graduation_year or not x_firstdegree_engineer_discipline or not x_discipline_s or not firstdegreefiles:
           #return http.request.redirect('/home')
           pe = post.get('1-x_applicant')
           peid = int(pe)
           msg = 'Data are not completed'
           if not peid:
              pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
              peid = pe.id
              pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
           return http.request.render('website.peverify', {'pedata': pedata,'peid': peid,'msg':msg,'sresult':1,'pdata':update_infos})
        else:
            for update_info in update_infos:
                firstuni = update_info.x_firstdegree_uni
                uniyear = update_info.x_firstdegree_graduation_year
                discipline = update_info.x_firstdegree_engineer_discipline
                attachment = update_info.x_firstdegree_attachment
                pattach = update_info.x_payment_attachment
            val = {'x_state':4,'x_form_status':4,}
            update_infos.sudo().write(val)
            id = post.get('1-x_applicant')
            peid = int(id)
            Job = request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
            verify_datas = self._process_verify_details(post)
            #for job in Job:
                #for verify_data in verify_datas:
                    #test = request.env['x_verify'].sudo().search([('id','=',verify_data['id'])])
                    #Job = test.sudo().write(verify_data)
            if Job:
               pedatas = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)]).unlink()
               if pedatas:
                  PE = request.env['x_verify']
                  for verify_data in verify_datas:
                      PE += PE.sudo().create(verify_data)
            hid = str(id)
            #pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
            useremail = update_infos.email_from
            message = "Your registration for APPLICATION FOR PROFESSIONAL ENGINEER with reg no PE-"+hid+" has been summited"
            subject = "Submit Application"
            y = send_email(useremail,message,subject)
            if y["state"]:
               return http.request.redirect('/my-record')
            #return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id})
            if not y["state"]:
               return request.redirect('/home')



    @http.route('/previousverify/', type='http', auth="public", methods=['POST'], website=True)
    def verify_back(self, **post):
       verify_datas = self._process_verify_details(post)
       #pe = request.website._website_form_last_record().sudo().id
       pe = post.get('1-x_applicant')
       peid = int(pe)
       Job = request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
       x_name = post.get('1-x_name')
       x_email = post.get('1-x_email')
       x_verifying_name = post.get('1-x_verifying_name')
       x_proengineer_no = post.get('1-x_proengineer_no')
       x_address_phone = post.get('1-x_address_phone')
       if x_name or x_email or x_verifying_name or x_proengineer_no or x_address_phone:
          if not Job:
             jb_datas = self._process_job(post)
             Jb = request.env['x_verify']
             for jb_data in jb_datas:
                 Jb += Jb.sudo().create(jb_data)
       if Job:
          pedatas = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)]).unlink()
          if pedatas:
             PE = request.env['x_verify']
             for verify_data in verify_datas:
                 PE += PE.sudo().create(verify_data)
          #for job in Job:
              #for verify_data in verify_datas:
                  #test = request.env['x_verify'].sudo().search([('id','=',verify_data['id'])])
                  #Job = test.sudo().write(verify_data)
       pedata = http.request.env['x_summary'].sudo().search([('x_applicant','=',peid)])
#       state = http.request.env['hr.applicant'].sudo().search([('id','=',pe)])
       pecount = http.request.env['x_summary'].sudo().search_count([('x_applicant','=',peid)])
       return http.request.render('website.pesummary',{'pedata':pedata,'peid':peid,'sresult':1,'pecount':pecount})

    def _process_verify_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())


    @http.route('/save_verify/', type='http', auth="public", methods=['POST'], website=True)
    def verify_confirm(self, **post):
       x_name = post.get('1-x_name')
       x_email = post.get('1-x_email')
       x_verifying_name = post.get('1-x_verifying_name')
       x_proengineer_no = post.get('1-x_proengineer_no')
       x_address_phone = post.get('1-x_address_phone')
       if x_name or x_email or x_verifying_name or x_proengineer_no or x_address_phone:
          verify_datas = self._process_verify_details(post)
          Verifier = request.env['x_verify']
          for verify_data in verify_datas:
              Verifier += Verifier.sudo().create(verify_data)
       pe = post.get('1-x_applicant')
       peid = int(pe)
       update_infos = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
       val = {'x_form_status':1}
       update_infos.sudo().write(val)
       pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
       if not peid and not pedata:
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
          peid = pe.id
       #return request.redirect('/previouspeproexperience3')
          pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
       return http.request.render('website.peverify', {'pedata': pedata,'peid': peid,'sresult':1,'saved':'1','pdata':update_infos})


    @http.route('/submit_summary/', type='http', auth="public", methods=['POST'], website=True)
    def summary_confirm1(self, **post):
        summary_datas = self._process_summary_back_details(post)
        pe = post.get('1-x_applicant')
        peid = int(pe)
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        #pe = request.website._website_form_last_record().sudo().id
        Job = request.env['x_summary'].sudo().search([('x_applicant','=',peid)])
        #for job in Job:
            #for summary_data in summary_datas:
                #test = request.env['x_summary'].sudo().search([('id','=',summary_data['id'])])
                #Job = test.sudo().write(summary_data)
        if Job:
           pedatas = http.request.env['x_summary'].sudo().search([('x_applicant','=',peid)]).unlink()
           if pedatas:
              PE = request.env['x_summary']
           for summary_data in summary_datas:
               PE += PE.sudo().create(summary_data)
        pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
        pecount = http.request.env['x_verify'].sudo().search_count([('x_applicant','=',peid)])
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        name = 1
        return http.request.render('website.peverify',{'pedata':pedata,'sresult':name,'peid':peid,'saved':'1','pecount':pecount,'pdata':pdata})


    @http.route('/previoussummary', type='http', auth="public", methods=['POST'], website=True)
    def previous_summary(self, **post):
        update_datas = self._process_summary_back_details(post)
        #pe = request.website._website_form_last_record().sudo().id
        pe = post.get('1-x_applicant')
        peid = int(pe)
        Job = request.env['x_summary'].sudo().search([('x_applicant','=',peid)])
        x_name = post.get('1-x_name')
        x_position = post.get('1-x_position')
        x_month = post.get('1-x_month')
        x_verifier_name = post.get('1-x_verifier_name')
        x_project = post.get('1-x_project')
        if x_name or x_position or x_month or x_verifier_name or x_project:
           if not Job:
              jb_datas = self._process_job(post)
              Jb = request.env['x_summary']
              for jb_data in jb_datas:
                  Jb += Jb.sudo().create(jb_data)
        #if Job:
           #for job in Job:
               #for update_data in update_datas:
                   #test = request.env['x_summary'].sudo().search([('id','=',update_data['id'])])
                   #Job = test.sudo().write(update_data)
        if Job:
           pedatas = http.request.env['x_summary'].sudo().search([('x_applicant','=',peid)]).unlink()
           if pedatas:
              summary_datas = self._process_job(post)
              PE = request.env['x_summary']
              for summary_data in summary_datas:
                  PE += PE.sudo().create(summary_data)
        pedata = http.request.env['x_involve'].sudo().search([('x_applicant','=',peid)])
        pecount = http.request.env['x_involve'].sudo().search_count([('x_applicant','=',peid)])
        #name = 0
        return http.request.render('website.peinvolvement',{'pedata':pedata,'sresult':1,'peid':peid,'pecount':pecount})

    def _process_summary_back_details(self, details):      
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
               global_values[field_name] = value
            else:
               registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())



    @http.route('/submit_involve', type='http', auth="public", methods=['POST'], website=True)
    def involve_confirm1(self, **post):
        involve_datas = self._process_involve_back_details(post)
        pe = post.get('1-x_applicant')
        peid = int(pe)
        #pe = request.website._website_form_last_record().sudo().id
        Job = request.env['x_involve'].sudo().search([('x_applicant','=',peid)])
        #for job in Job:
            #for involve_data in involve_datas:
                #test = request.env['x_involve'].sudo().search([('id','=',involve_data['id'])])
                #Job = test.sudo().write(involve_data)
        pedatas = http.request.env['x_involve'].sudo().search([('x_applicant','=',peid)]).unlink()
        if pedatas:
           PE = request.env['x_involve']
           for verify_data in involve_datas:
               PE += PE.sudo().create(verify_data)
        pedata = http.request.env['x_summary'].sudo().search([('x_applicant','=',peid)])
        pecount = http.request.env['x_summary'].sudo().search_count([('x_applicant','=',peid)])
        name = 1
        return http.request.render('website.pesummary',{'pedata':pedata,'sresult':name,'peid':peid,'pecount':pecount})



    @http.route('/save_involve/', type='http', auth="public", methods=['POST'], website=True)
    def involve_confirm(self, **post):
        x_name = post.get('1-x_name')
        x_organization_name = post.get('1-x_organization_name')
        x_started_date = post.get('1-x_started_date')
        x_finished_date = post.get('1-x_finished_date')
        x_position_title = post.get('1-x_position_title')
        x_verifier_name = post.get('1-x_verifier_name')
        x_verifier_relation = post.get('1-x_verifier_relation')
        x_verifier_phone = post.get('1-x_verifier_phone')
        if x_name or x_organization_name or x_started_date or x_finished_date or x_position_title or x_verifier_name or x_verifier_relation or x_verifier_phone:
           involve_datas = self._process_involve_details(post)
           Involve = request.env['x_involve']
           for involve_data in involve_datas:
               Involve += Involve.sudo().create(involve_data)
        pe = post.get('1-x_applicant')
        peid = int(pe)
        if not peid:
           pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
           peid = pe.id
        pedata = http.request.env['x_summary'].sudo().search([('x_applicant','=',peid)])
        return http.request.render('website.pesummary',{'sresult':1,'peid':peid,'regsave':1})
        #return request.redirect('/peproexperience2')

    def _process_involve_details(self, details):      
         registrations = {}
         global_values = {}
         for key, value in details.items():
             counter, field_name = key.split('-', 1)
             if counter == '0':
                global_values[field_name] = value
             else:
                registrations.setdefault(counter, dict())[field_name] = value
         for key, value in global_values.items():
             for registration in registrations.values():
                 registration[key] = value
         return list(registrations.values())




    @http.route('/previouspeproexperience', type='http', auth="public", methods=['POST'], website=True)
    def previous_peproexperience(self, **post):
        involve_datas = self._process_involve_back_details(post)
        pe = post.get('1-x_applicant')
        peid = int(pe)
        #pe = request.website._website_form_last_record().sudo().id
        Job = request.env['x_involve'].sudo().search([('x_applicant','=',peid)])
        x_name = post.get('1-x_name')
        x_organization_name = post.get('1-x_organization_name')
        x_started_date = post.get('1-x_started_date')
        x_finished_date = post.get('1-x_finished_date')
        x_position_title = post.get('1-x_position_title')
        x_verifier_name = post.get('1-x_verifier_name')
        x_verifier_relation = post.get('1-x_verifier_relation')
        x_verifier_phone = post.get('1-x_verifier_phone')
        if x_name or x_organization_name or x_started_date or x_finished_date or x_position_title or x_verifier_name or x_verifier_relation or x_verifier_phone:
           if not Job:
              jb_datas = self._process_job(post)
              Jb = request.env['x_involve']
              for jb_data in jb_datas:
                  Jb += Jb.sudo().create(jb_data)
        #if Job:
           #for job in Job:
               #for involve_data in involve_datas:
                   #test = request.env['x_involve'].sudo().search([('id','=',involve_data['id'])])
                   #Job = test.sudo().write(involve_data)
        if Job:
           pedatas = http.request.env['x_involve'].sudo().search([('x_applicant','=',peid)]).unlink()
           if pedatas:
              PE = request.env['x_involve']
              for verify_data in involve_datas:
                  PE += PE.sudo().create(verify_data)
        pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',peid)])
        return http.request.render('website.peproexperienceforms',{'pedata':pedata,'peid':peid,'sresult':1})

    def _process_involve_back_details(self, details):        
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())


    @http.route(['/acperegistrationform'], type='http', auth='public', website=True)
    def acpe_data(self, **kw):
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        #acpeid = request.website._website_form_last_record().sudo().id
        #acpedata = http.request.env['hr.applicant'].sudo().search([('id','=',acpeid)])
        #academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',acpedata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        #practicefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',acpedata.id),('res_model','=','hr.applicant'),('x_field','=','x_practice')])
        todaydate =  fields.Datetime.now()
        uid = request.uid
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)])
        if pdata:
     	   lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.acperegistrationform', {'nrc':nrc,'ddata':ddata,'todaydate':todaydate,'lid':lid,'uid':uid})


    @http.route('/acpeproexperience/', website=True, auth='public', method='POST')
    def qualifications_function4(self, **kw):
        name = kw.get('name')
        acpeid = kw.get('id')
        if not name:
            name = 1
        if not acpeid:
           acpe = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)], order="id desc", limit=1)[0]
           acpeid = acpe.id
           #acpeid = request.website._website_form_last_record().sudo().id
        return http.request.render('website.acpeproexperience',{'sresult':name,'acpeid':acpeid})

    @http.route('/previousacperegistration', website=True, auth='public', type='http',methods=['POST'])
    def back_step1(self, **post):
        #name = kw.get('name')
        #if not name:
            #name = 1
        #peid = request.website._website_form_last_record().sudo().id
        pe = post.get('1-x_applicant')
        peid = int(pe)
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pedata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        practicefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pedata.id),('res_model','=','hr.applicant'),('x_field','=','x_practice')])
        if post and request.httprequest.method == 'POST':
           job_datas = self._process_job(post)
           #pid = int(peid)
           Job = request.env['x_proexperience'].sudo().search([('x_applicant','=',peid)])
           expname = post.get('1-x_name')
           if expname:
              if not Job:
                 jb_datas = self._process_job(post)
                 Jb = request.env['x_proexperience']
                 for jb_data in jb_datas:
                     Jb += Jb.sudo().create(jb_data)
           
           #if Job:
              #for job in Job:
                  #for job_data in job_datas:
                      #test = request.env['x_proexperience'].sudo().search([('id','=',job_data['id'])])
                      #Job = test.sudo().write(job_data)
           acpedatas = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',peid)]).unlink()
           if acpedatas:
              ACPE = request.env['x_proexperience']
              for verify_data in job_datas:
                  ACPE += ACPE.sudo().create(verify_data)
        return http.request.render('website.acperegistrationform',{'pdata':pedata,'ddata':ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'practicefiles':practicefiles})

    @http.route('/reviewacperegistration', website=True, auth='public', method='POST')
    def back_stepacpe1(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        peid = kw.get('id')
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        type = 'ACPE'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':pedata,'ddata':ddata,'sresult':name,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/reviewacpeproexperience', type='http',website=True, auth='public', methods=['POST'])
    def review_acpeproexperience(self, **post):
        acpeid = post.get('id')
        aid = int(acpeid)
        rtcdata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',aid)])
        acpecount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',aid)])
        acpedata = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
        return http.request.render('website.review-acpeproexperience',{'rtcdata':rtcdata,'acpeid':acpeid,'sresult':1,'acpedata':acpedata,'acpecount':acpecount})

    @http.route('/update_acperegistrationform', type='http', auth="public", methods=['POST'], website=True)
    def update_acpe_registration1(self, **post):
        #rtcid = request.website._website_form_last_record().sudo().id
        id = post.get('id')
        rtc = request.env['hr.applicant'].sudo().search([('id','=',id)])
        #history = http.request.env['x_history'].sudo().search([])
        #hvalue = { 'x_state':'4', 'x_applicant_id': id}
        #history.sudo().create(hvalue)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        practicefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_practice')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_practice' in request.params:
              attached_files = request.httprequest.files.getlist('x_practice')
              import base64
              if attached_files:
                 practicefiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  practicefiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': id,
                        'type': 'binary',
                        'x_field': 'x_practice',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo

        if post.get('x_firstdegree_filename'):
           x_firstdegree_filename = post.get('x_firstdegree_filename')
        if not post.get('x_firstdegree_filename'):
           x_firstdegree_filename = rtc.x_firstdegree_filename


        if post.get('x_practice_certificate_attachment'):
           FileStorage = post.get('x_practice_certificate_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_practice_certificate_attachment  = base64.encodestring(FileData)
        if not post.get('x_practice_certificate_attachment'):
            x_practice_certificate_attachment = rtc.x_practice_certificate_attachment
        if post.get('x_practice_certificate_attachment_name'):
           x_practice_certificate_attachment_name = post.get('x_practice_certificate_attachment_name')
        if not post.get('x_practice_certificate_attachment_name'):
           x_practice_certificate_attachment_name = rtc.x_practice_certificate_attachment_name
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = rtc.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = rtc.x_other_attachment_name_1


        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = rtc.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = rtc.x_other_attachment_name_2


        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = rtc.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = rtc.x_other_attachment_name_3

        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = rtc.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = rtc.x_other_attachment_name_4
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     'x_reg_no':post.get('x_reg_no'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_address_en':post.get('x_address_en'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_experience_year':post.get('x_experience_year'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_academic_qualification':post.get('x_academic_qualification'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                     'x_firstdegree_filename':x_firstdegree_filename,
                     'x_practice_certificate_attachment_name':x_practice_certificate_attachment_name,
                     'x_practice_certificate_attachment':x_practice_certificate_attachment,
                     'x_office_address':post.get('x_office_address'),
                     'x_fax_no':post.get('x_fax_no'),
                     'x_identity_card_date':post.get('x_identity_card_date'),
                     'x_practice_certificate_no':post.get('x_practice_certificate_no'),
                     'x_registration_date':post.get('x_registration_date'),
                     'x_date_of_previous_application':post.get('x_date_of_previous_application'),
                     'x_work_fifteen_year':post.get('x_work_fifteen_year'),
                     'x_meet_requirement':post.get('x_meet_requirement'),
                     'x_no_discipline':post.get('x_no_discipline'),
                     'x_other':post.get('x_other'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc1mm':post.get('x_nrc1mm'),
                     'x_nrc2mm':post.get('x_nrc2mm'),
                     'x_nrc3mm':post.get('x_nrc3mm'),
                     'x_nrc4mm':post.get('x_nrc4mm'),
                     'partner_id':post.get('partner_id'),
                     'x_discipline_s':post.get('x_discipline_s'),
                     'x_other_attachment_1':x_other_attachment_1,
                     'x_other_attachment_name_1':x_other_attachment_name_1,
                     'x_other_attachment_2':x_other_attachment_2,
                     'x_other_attachment_name_2':x_other_attachment_name_2,
                     'x_other_attachment_3':x_other_attachment_3,
                     'x_other_attachment_name_3':x_other_attachment_name_3,
                     'x_other_attachment_4':x_other_attachment_4,
                     'x_other_attachment_name_4':x_other_attachment_name_4,
                     'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                     'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                     'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                     'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                    }

        rtc.sudo().write(values)
        name = 1
        testfiles = request.env['ir.attachment'].sudo().search([('res_id','=',264)])
        aid = int(id)
        rtcdata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',aid)])
        acpecount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',aid)])
        return http.request.render('website.acpeproexperience',{'rtcdata':rtcdata, 'testfiles':testfiles,'sresult':name,'acpeid':id,'acpecount':acpecount})




    @http.route('/job_acpe/', type='http', auth="public", methods=['POST'], website=True)
    def job_acpe(self, **post):
        job_datas = self.acpe_process_job_details(post)
        Job = request.env['x_proexperience']
        for job_data in job_datas:
            Job += Job.sudo().create(job_data)
        rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['x_involve'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        return http.request.render('website.acpeproexperience',{'rtcdata':rtcdata,'ddata':ddata,'nrc':nrc})


    def acpe_process_job_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route(['/previousacpeproexperience'], type='http', auth='public', website=True)
    def back_verify_acpe(self, **kw):
         name = kw.get('name')
         if not name:
             name = 1
         peid = kw.get('id')
        # peid = request.website._website_form_last_record().sudo().id
         pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',peid)])
         pcount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',peid)])
         acpe = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)], order="id desc", limit=1)[0]
         acpeid = acpe.id
         return http.request.render('website.acpeproexperience', {'rtcdata': pedata, 'pcount': pcount,'pid': peid,'sresult':name,'acpeid':acpeid})

    @http.route(['/previousacpeproexperience1'], type='http', auth='public', website=True)
    def back_verify_acpe1(self, **kw):
         name = kw.get('name')
         if not name:
             name = 1
         peid = kw.get('acpeid')
         acpid = int(peid)
        # peid = request.website._website_form_last_record().sudo().id
         pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',acpid)])
         pcount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',acpid)])
         return http.request.render('website.acpeproexperience', {'rtcdata': pedata, 'pcount': pcount,'pid': acpid,'sresult':name})


    @http.route('/save_and_previous_acperegistration', type='http', auth="public", methods=['POST'], website=True)
    def involve_back_save_acpe(self, **post):
        job_datas = self._proce_acpe_back_details(post)
        Job = request.env['x_proexperience']
        for job_data in job_datas:
            Job += Job.sudo().create(job_data)
        return request.redirect('/previousacperegistration')

    def _proce_acpe_back_details(self, details):
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
               global_values[field_name] = value
            else:
               registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())



    @http.route('/save_acpeproexperience', type='http', auth="public", methods=['POST'], website=True)
    def involve_back_update_acpe(self, **post):
        acpid = post.get('1-x_applicant')
        acpeid = str(acpid)
        apid = int(acpid)
        job_datas = self.acpe_process_job_details(post)
        Job = request.env['x_proexperience']
        for job_data in job_datas:
            Job += Job.sudo().create(job_data)
        #return http.request.render('website.testdelete',{'Job':Job,'acpid':acpid,'acpeid':acpeid})
        pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',apid)])
        acpecount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',apid)])
        return http.request.render('website.acpeproexperience', {'rtcdata': pedata,'acpeid': acpeid,'sresult': 1,'acpecount':acpecount})
        #return request.redirect('/previousacpeproexperience1?msg1=2&acpeid='+acpeid) 
 
    def _process_acpe_back_details(self, details):
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
               global_values[field_name] = value
            else:
               registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())


    @http.route('/submit_acpeproexperience/', type='http', auth="public", methods=['POST'], website=True)
    def verify_acperegistration_submit(self, **post):
        verify_datas = self._process_verify_acpe_details(post)
        id = post.get('1-x_applicant')
        #id = post.get('id')
        aid = int(id)
        #pe = request.website._website_form_last_record().sudo().id
        Job = request.env['x_proexperience'].sudo().search([('x_applicant','=',aid)])
        #pe = request.website._website_form_last_record().sudo().id
        update_infos = request.env['hr.applicant'].sudo().search([('id','=',aid)])
        jid = update_infos.job_id.id
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'4', 'x_applicant_id': aid, 'x_job_id':jid }
        history.sudo().create(hvalue)
        val = {'x_state':4,'x_form_status':4,}
        update_infos.sudo().write(val)
        acpedatas = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',aid)]).unlink()
        if acpedatas:
           ACPE = request.env['x_proexperience']
           for verify_data in verify_datas:
               ACPE += ACPE.sudo().create(verify_data)
        #if not Job:
           #for job in Job:
               #for verify_data in verify_datas:
                   #test = request.env['x_proexperience'].sudo().search([('id','=',verify_data['id'])])
                   #Job = test.sudo().create(verify_data)
        type = 'ACPE'
        hid = str(aid)
        #pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = update_infos.email_from
        message = "Your registration for APPLICATION FOR  ASEAN CHARTERED PROFESSIONAL ENGINEER (ACPE) with reg no ACPE-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
        if not y["state"]:
           return request.redirect('/home')



    def _process_verify_acpe_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route(['/agtechregistrationform'], type='http', auth='public', website=True)
    def agtech_data(self, **kw):
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.agtechregistrationform', {'nrc':nrc,'nrcmm':nrcmm,'ddata':ddata,'todaydate':todaydate,'lid':lid})

    @http.route('/previousagtechregistration', website=True, auth='public', method='POST')
    def previous_agtech(self, **kw):
        #id = kw.get('applicant')
        rtcid = kw.get('id')
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        type = 'AGTech'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':rtcdata,'nrc':nrc,'nrcmm':nrcmm,'ddata':ddata})


    @http.route('/save_agtechregistrationform', website=True, auth='public', method='POST')
    def save_agtechregistration(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.agtechregistrationform',{'rtcdata':rtcdata,'ddata':ddata,'sresult':name,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles})

    @http.route('/submit_agtechregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_agtechregistration1(self, **post):
       # rtcid = request.website._website_form_last_record().sudo().id
        id = post.get('id')
        date =  fields.Datetime.now()
        adate = date.date()
        rtc = request.env['hr.applicant'].sudo().search([('id','=',id)])
        dis = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value1 = {
                           'x_discipline':[(6, 0, val)]
                    }
                    value2 = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           #ALLOWED_IMAGE_EXTENSIONS = ['jpg','png']
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           #ALLOWED_IMAGE_EXTENSIONS = ['jpg','png']
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if post.get('x_firstdegree_attachment'):
           FileStorage = post.get('x_firstdegree_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_firstdegree_attachment  = base64.encodestring(FileData)
        if not post.get('x_firstdegree_attachment'):
               x_firstdegree_attachment = rtc.x_firstdegree_attachment
        if post.get('x_firstdegree_filename'):
           x_firstdegree_filename = post.get('x_firstdegree_filename')
        if not post.get('x_firstdegree_filename'):
           x_firstdegree_filename = rtc.x_firstdegree_filename
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = rtc.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = rtc.x_other_attachment_name_1
        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = rtc.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = rtc.x_other_attachment_name_2
        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = rtc.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = rtc.x_other_attachment_name_3
        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = rtc.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = rtc.x_other_attachment_name_4
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     'x_name_mm':post.get('x_name_mm'),
                     'x_father_en':post.get('x_father_en'),
		     'x_father_mm':post.get('x_father_mm'),
                     'x_reg_no':post.get('x_reg_no'),
                     'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_address_en':post.get('x_address_en'),
                     'x_address_mm':post.get('x_address_mm'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_academic_qualification':post.get('x_academic_qualification'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                     'x_firstdegree_attachment':x_firstdegree_attachment,
                     'x_firstdegree_filename':x_firstdegree_filename,
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc1mm':post.get('x_nrc1mm'),
                     'x_nrc2mm':post.get('x_nrc2mm'),
                     'x_nrc3mm':post.get('x_nrc3mm'),
                     'x_nrc4mm':post.get('x_nrc4mm'),
                     'partner_id':post.get('partner_id'),
                     'x_state':4,
                     'x_form_status':4,
                     'x_discipline_s':post.get('x_discipline_s'),
                     'x_applied_date': adate,
                     'x_other_attachment_1':x_other_attachment_1,
                     'x_other_attachment_name_1':x_other_attachment_name_1,
                     'x_other_attachment_2':x_other_attachment_2,
                     'x_other_attachment_name_2':x_other_attachment_name_2,
                     'x_other_attachment_3':x_other_attachment_3,
                     'x_other_attachment_name_3':x_other_attachment_name_3,
                     'x_other_attachment_4':x_other_attachment_4,
                     'x_other_attachment_name_4':x_other_attachment_name_4,
                     'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                     'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                     'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                     'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                    }
       # rtc.sudo().write(value2)
       # rtc.sudo().write(value1)
        rtc.sudo().write(values)
        type = 'AGTech'
        hid = ' '+id+' '
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for apprentice engineer certificate with reg no AGTech-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
          # return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
        if not y["state"]:
           return request.redirect('/home')


    @http.route(['/aecregistrationform'], type='http', auth='public', website=True)
    def aec_data(self, **kw):
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          ddata = http.request.env['x_discipline'].sudo().search([])
          todaydate =  fields.Datetime.now()
          pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',9)])
          if pdata:
             lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',9)], order="id desc", limit=1)[0]
          if not pdata:
             lid = ' '
          return http.request.render('website.aecregistrationform', {'nrc':nrc,'nrcmm':nrcmm,'ddata':ddata,'todaydate':todaydate,'lid':lid})


    @http.route('/previousaecregistration', website=True, auth='public', method='POST')
    def previous_aec(self, **kw):
        #id = kw.get('applicant')
        rtcid = id = kw.get('id')
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        type = 'AEC'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':rtcdata,'nrc':nrc,'nrcmm':nrcmm,'ddata':ddata})

    @http.route('/save_aecregistrationform', website=True, auth='public', method='POST')
    def save_aecregistration(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.aecregistrationform',{'rtcdata':rtcdata,'ddata':ddata,'sresult':name,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles})

    @http.route('/submit_aecregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_aecregistration1(self, **post):
       # rtcid = request.website._website_form_last_record().sudo().id
        id = post.get('id')
        date =  fields.Datetime.now()
        adate = date.date()
        rtc = request.env['hr.applicant'].sudo().search([('id','=',id)])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        dis = http.request.env['x_discipline'].sudo().search([])
        date =  fields.Datetime.now()
        adate = date.date()
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'4', 'x_applicant_id': id, 'x_job_id': 9}
        history.sudo().create(hvalue)
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value = {
                           'x_discipline':[(6, 0, val)]
                    }
                    vals = {
                           'x_discipline':[(5,)]
                   }
       # if dis:
            #if post:
                #res = 'no data'

                #if post.get('x_discipline'):
                    #list_id = request.httprequest.form.getlist('x_discipline')
                    #count = 0
                    #val = []
                    #for mm in list_id:
                        #val.append(list_id[count])
                        #count = count + 1
                    #value1 = {
                           #'x_discipline':[(6, 0, val)]
                    #}
                    #value2 = {
                           #'x_discipline':[(5,)]
                   #}
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })

        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if post.get('x_firstdegree_attachment'):
           FileStorage = post.get('x_firstdegree_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_firstdegree_attachment  = base64.encodestring(FileData)
        if not post.get('x_firstdegree_attachment'):
               x_firstdegree_attachment = rtc.x_firstdegree_attachment
        if post.get('x_firstdegree_filename'):
           x_firstdegree_filename = post.get('x_firstdegree_filename')
        if not post.get('x_firstdegree_filename'):
           x_firstdegree_filename = rtc.x_firstdegree_filename
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = rtc.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = rtc.x_other_attachment_name_1


        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = rtc.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = rtc.x_other_attachment_name_2


        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = rtc.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = rtc.x_other_attachment_name_3

        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = rtc.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = rtc.x_other_attachment_name_4
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     'x_name_mm':post.get('x_name_mm'),
                     'x_father_en':post.get('x_father_en'),
		     'x_father_mm':post.get('x_father_mm'),
                     'x_reg_no':post.get('x_reg_no'),
                     'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_address_en':post.get('x_address_en'),
                     'x_address_mm':post.get('x_address_mm'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_academic_qualification':post.get('x_academic_qualification'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                     'x_firstdegree_attachment':x_firstdegree_attachment,
                     'x_firstdegree_filename':x_firstdegree_filename,
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc1mm':post.get('x_nrc1mm'),
                     'x_nrc2mm':post.get('x_nrc2mm'),
                     'x_nrc3mm':post.get('x_nrc3mm'),
                     'x_nrc4mm':post.get('x_nrc4mm'),
                     'partner_id':post.get('partner_id'),
                     'x_state':4,
                     'x_discipline_s':post.get('x_discipline_s'),
                     'x_form_status':4,
                     'x_applied_date': adate,
                     'x_other_attachment_1':x_other_attachment_1,
                     'x_other_attachment_name_1':x_other_attachment_name_1,
                     'x_other_attachment_2':x_other_attachment_2,
                     'x_other_attachment_name_2':x_other_attachment_name_2,
                     'x_other_attachment_3':x_other_attachment_3,
                     'x_other_attachment_name_3':x_other_attachment_name_3,
                     'x_other_attachment_4':x_other_attachment_4,
                     'x_other_attachment_name_4':x_other_attachment_name_4,
                     'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                     'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                     'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                     'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                    }

       # rtc.sudo().write(value2)
       # rtc.sudo().write(value1)
        rtc.sudo().write(values)
        type = 'AEC'
        hid = ' '+id+' '
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for apprentice engineer certificate with reg no AEC-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
           #return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id})
        if not y["state"]:
           return request.redirect('/home')


    @http.route(['/rerenewalregistrationform'], type='http', auth='public', website=True)
    def rerenewal__data(self, **kw):
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          return http.request.render('website.rerenewalregistrationform', {'nrc':nrc})

    @http.route('/save_rerenewalregistrationform', website=True, auth='public', method='POST')
    def save_rerenewalregistration(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        return http.request.render('website.rerenewalregistrationform',{'rtcdata':rtcdata,'ddata':ddata,'sresult':name,'nrc':nrc})
  
    @http.route('/previousrerenewalregistration', website=True, auth='public', method='POST')
    def previous_rerenewal(self, **kw):
        #id = kw.get('applicant')
        rtcid = kw.get('id')
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        type = 'RERENEWAL'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':rtcdata,'nrc':nrc})

    @http.route('/submit_rerenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rerenewalregistration1(self, **post):
        rtcid = request.website._website_form_last_record().sudo().id
        id = post.get('id')
        rtc = request.env['hr.applicant'].sudo().search([('id','=',id)])
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo

        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     'x_reg_no':post.get('x_reg_no'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_address_en':post.get('x_address_en'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                     'x_pe_registration_valid_date':post.get('x_pe_registration_valid_date'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc1mm':post.get('x_nrc1mm'),
                     'x_nrc2mm':post.get('x_nrc2mm'),
                     'x_nrc3mm':post.get('x_nrc3mm'),
                     'x_nrc4mm':post.get('x_nrc4mm'),
                     'partner_id':post.get('partner_id'),
                     'x_state':post.get('x_state'),                   
                    }

        rtc.sudo().write(values)
        type = 'RERENEWAL'
        return http.request.render('website_hr_recruitment.thankyou', {'type':type})


    @http.route(['/perenewalregistrationform'], type='http', auth='public', website=True)
    def perenewal__data(self, **kw):
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        return http.request.render('website.perenewalregistrationform', {'nrc':nrc,'sample':sample})

    @http.route('/save_perenewalregistrationform', website=True, auth='public', method='POST')
    def save_perenewalregistration(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        return http.request.render('website.perenewalregistrationform',{'rtcdata':rtcdata,'ddata':ddata,'sresult':name,'nrc':nrc})

    @http.route('/previousperenewalregistration', website=True, auth='public', method='POST')
    def previous_perenewal(self, **kw):
        #id = kw.get('applicant')
        rtcid = kw.get('id')
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        type = 'PERENEWAL'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':rtcdata,'nrc':nrc})

    @http.route('/transfer_renewal', type='http', auth="public", methods=['POST'], website=True)
    def transfer_renewal(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        old_data.sudo().write({'x_state':'24','x_cpd_status': 1})
        remark = post.get('t_remark')
        if jobid == 1:
           return http.request.redirect('/pe-renew-list')
        if jobid == 5:
           return http.request.redirect('/rsec-renew-list')
        if jobid == 6:
           return http.request.redirect('/rle-renew-list')
        if jobid == 8:
           return http.request.redirect('/rfpe-renew-list')
        if jobid == 10:
           return http.request.redirect('/rec-renew-list')

    @http.route('/renewal_fine', type='http', auth="public", methods=['POST'], website=True)
    def renewal_fine(self, **post):
        jjobid = post.get('jid')
        jobid = int(jjobid)
        id = post.get('id')
        remark = post.get('f_remark')
        userid = request.env.user.partner_id.id
        todaydate =  fields.Datetime.now()
        Applicant = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aid = Applicant.id        
        apid = int(aid)
        useremail = Applicant.email_from
        Applicant.sudo().write({'x_fine_status':1})
        pay = http.request.env['x_application_payment'].sudo().search([('x_applicant_id','=',apid)])
        val = {
               'x_applicant_id': aid,
               'x_payment_status': 'Pending',
               'x_application_payment_id': pay.id,
               'x_apply_date': todaydate,
               'x_remark':remark,
               'x_job_id': jobid,
               'x_partner_id': userid,
               }
        aapay = http.request.env['x_applicant_application_payment'].sudo().create(val)        
        aaid = aapay.id
        aaid1 = str(aaid)
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
        durl = dynamic_url.x_name
        if remark:
           message = "Your need to pay fine fee. Please pay at "+durl+aaid1+". <br>Remark "+remark
        if not remark:
           message = "Your need to pay fine fee. Please pay at "+durl+aaid1
        subject = "Renewal Fine Fee"
        y = send_email(useremail,message,subject)
        if y["state"]:
           if jobid == 1:
              return http.request.redirect('/pe-renew-list')
           if jobid == 5:
              return http.request.redirect('/rsec-renew-list')
           if jobid == 6:
              return http.request.redirect('/rle-renew-list')
           if jobid == 8:
              return http.request.redirect('/rfpe-renew-list')
           if jobid == 10:
              return http.request.redirect('/rec-renew-list')
        if not y["state"]:
           return http.request.redirect('/home')


    @http.route('/renewal_confirm', type='http', auth="public", methods=['POST'], website=True)
    def renewal_confirm(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        old_data.sudo().write({'x_state':'25'})
        remark = post.get('c_remark')
        if jobid == 1:
           return http.request.redirect('/pe-renew-list')
        if jobid == 5:
           return http.request.redirect('/rsec-renew-list')
        if jobid == 6:
           return http.request.redirect('/rle-renew-list')
        if jobid == 8:
           return http.request.redirect('/rfpe-renew-list')
        if jobid == 10:
           return http.request.redirect('/rec-renew-list')


    @http.route('/cpd_resubmit_renewal', type='http', auth="public", methods=['POST'], website=True)
    def cpd_resubmit_renewal(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        old_data.sudo().write({'x_cpd_status':0})
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','resubmit')])
        durl = dynamic_url.x_name
        url = durl+id
        useremail = old_data.email_from
        remark = post.get('cpd_remark')
        if remark:
           message = "Your form is not correct. Please refill at "+url+". <br>Remark "+remark
        if not remark:
           message = "Your form is not correct. Please refill at "+url
        subject = "Resubmit Renewal"
        y = send_email(useremail,message,subject)
        if y["state"]:
           if jobid == 1:
              return http.request.redirect('/pe-renew-list')
           if jobid == 5:
              return http.request.redirect('/rsec-renew-list')
           if jobid == 6:
              return http.request.redirect('/rle-renew-list')
           if jobid == 8:
              return http.request.redirect('/rfpe-renew-list')
           if jobid == 10:
              return http.request.redirect('/rec-renew-list')
        if not y["state"]:
           return http.request.redirect('/home')

    @http.route('/resubmit_renewal', type='http', auth="public", methods=['POST'], website=True)
    def resubmit_renewal(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        old_data.sudo().write({'x_state':'23'})
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','resubmit')])
        durl = dynamic_url.x_name
        url = durl+id
        useremail = old_data.email_from
        remark = post.get('r_remark')
        if remark:
           message = "Your form is not correct. Please refill at "+url+". <br>Remark "+remark
        if not remark:
           message = "Your form is not correct. Please refill at "+url
        subject = "Resubmit Renewal"
        y = send_email(useremail,message,subject)
        if y["state"]:
           if jobid == 1:
              return http.request.redirect('/pe-renew-list')
           if jobid == 5:
              return http.request.redirect('/rsec-renew-list')
           if jobid == 6:
              return http.request.redirect('/rle-renew-list')
           if jobid == 8:
              return http.request.redirect('/rfpe-renew-list')
           if jobid == 10:
              return http.request.redirect('/rec-renew-list')
        if not y["state"]:
           return http.request.redirect('/home')

    @http.route('/submit_rlerenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rlerenewalregistration(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        re_values = {
                   'x_applicant_id':old_data.id,
                   'x_job_id':old_data.job_id.id,
                   'x_approval_no': old_data.x_approval_no,
                   'x_reg_no': old_data.x_reg_no,
                   'x_name':old_data.partner_name,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_address_en':old_data.x_address_en,
                   'x_nrc1en':old_data.x_nrc1en,
                   'x_nrc2en':old_data.x_nrc2en,
                   'x_nrc3en':old_data.x_nrc3en,
                   'x_nrc4en':old_data.x_nrc4en,
                   'x_engineering_discipline':old_data.x_engineering_discipline,
                   'x_partner_phone':old_data.partner_phone,
                   'x_email_from':old_data.email_from,
                   'x_passportattachment_filename':old_data.x_passportattachment_filename,
                   'x_passportattachment':old_data.x_passportattachment,
                   'x_photo':old_data.x_photo,
                   'x_renewal_date': todaydate,
                   'x_passportexpiredate': old_data.x_passportexpiredate,
                   'x_lcompany': old_data.x_lcompany,
                   'x_gender': old_data.x_gender,
                   'x_citizenship': old_data.x_citizenship,
                   'x_passportexpiredate': old_data.x_passportexpiredate,
                   'x_rle_registration_valid_date': post.get('x_rle_registration_valid_date'),
                    }
        renwal_history = http.request.env['x_renewal_history'].sudo().create(re_values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': old_data.id, 'x_job_id': old_data.job_id.id}
        history.sudo().create(hvalue)
        renew_val = { 'x_user_id':old_data.partner_id.id, 'x_applicant_id': old_data.id, 'x_renewal_date': todaydate,'x_application_type':old_data.job_id.id,'x_reg_no': old_data.x_reg_no, 'x_approval_no': old_data.x_approval_no}
        renew = http.request.env['x_renewal'].sudo().create(renew_val)
        #id = post.get('id')
        rtc = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_passportattachment'):
           FileStorage = post.get('x_passportattachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_passportattachment = base64.encodestring(FileData)
        if not post.get('x_passportattachment'):
           x_passportattachment = rtc.x_passportattachment
        if post.get('x_passportattachment_filename'):
           x_passportattachment_filename = post.get('x_passportattachment_filename')
        if not post.get('x_passportattachment_filename'):
           x_passportattachment_filename = rtc.x_passportattachment_filename
        if post.get('x_rle_attachment'):
           FileStorage = post.get('x_rle_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
              return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rle_attachment = base64.encodestring(FileData)
        if not post.get('x_rle_attachment'):
           x_rle_attachment = rtc.x_rle_attachment
        if post.get('x_rle_attachment_filename'):
           x_rle_attachment_filename = post.get('x_rle_attachment_filename')
        if not post.get('x_rle_attachment_filename'):
           x_rle_attachment_filename = rtc.x_rle_attachment_filename
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_passportno':post.get('x_passportno'),
                     'x_dob':post.get('x_dob'),
                     'x_engineering_discipline':post.get('x_engineering_discipline'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_passportattachment':x_passportattachment,
                     'x_passportattachment_filename':x_passportattachment_filename,
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_passportexpiredate': post.get('x_passportexpiredate'),
                     'x_lcompany': post.get('x_lcompany'),
                     'x_gender': post.get('x_gender'),
                     'x_citizenship': post.get('x_citizenship'),
                     'x_rle_attachment': x_rle_attachment,
                     'x_rle_attachment_filename': x_rle_attachment_filename,
                     'x_rle_registration_valid_date': post.get('x_rle_registration_valid_date'),
                    }
           rtc.sudo().write(values)
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',13),('x_application_id','=',jobid)],limit=1)
           date =  fields.Datetime.now()
           val = {
                    'x_applicant_id': rtc.id,
                    'x_payment_status': 'Pending',
                    'x_application_payment_id': apay.id,
                    'x_apply_date': date,
                    'x_remark':'RLE Renewal',
                    'x_job_id': rtc.job_id.id,
                    'x_partner_id': rtc.partner_id.id,
                  }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(val)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           payid = Pay.id
           payurl = durl+str(payid)
           message = "Your renewal form is renewed and please pay payment "+payurl
           subject = "Renew Application"
           useremail = old_data.email_from
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect(payurl)
           if not y["state"]:
              return request.redirect('/home')


    @http.route('/submit_rfperenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rfperenewalregistration(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        re_values = {
                   'x_applicant_id':old_data.id,
                   'x_job_id':old_data.job_id.id,
                   'x_approval_no': old_data.x_approval_no,
                   'x_reg_no': old_data.x_reg_no,
                   'x_name':old_data.partner_name,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_address_en':old_data.x_address_en,
                   'x_nrc1en':old_data.x_nrc1en,
                   'x_nrc2en':old_data.x_nrc2en,
                   'x_nrc3en':old_data.x_nrc3en,
                   'x_nrc4en':old_data.x_nrc4en,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_dob':old_data.x_dob,
                   #'x_pe_registration_valid_date':old_data.x_pe_registration_valid_date,
                   'x_engineering_discipline':old_data.x_engineering_discipline,
                   'x_partner_phone':old_data.partner_phone,
                   'x_email_from':old_data.email_from,
                   'x_passportattachment_filename':old_data.x_passportattachment_filename,
                   'x_passportattachment':old_data.x_passportattachment,
                   'x_photo':old_data.x_photo,
                   'x_renewal_date': todaydate,
                   'x_passportexpiredate': old_data.x_passportexpiredate,
                   'x_lcompany': old_data.x_lcompany,
                   'x_gender': old_data.x_gender,
                   'x_citizenship': old_data.x_citizenship,
                   }
        renwal_history = http.request.env['x_renewal_history'].sudo().create(re_values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': old_data.id, 'x_job_id': old_data.job_id.id}
        history.sudo().create(hvalue)
        renew_val = { 'x_user_id':old_data.partner_id.id, 'x_applicant_id': old_data.id, 'x_renewal_date': todaydate,'x_application_type':old_data.job_id.id,'x_reg_no': old_data.x_reg_no, 'x_approval_no': old_data.x_approval_no}
        renew = http.request.env['x_renewal'].sudo().create(renew_val)
        #id = post.get('id')
        rtc = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_passportattachment'):
           FileStorage = post.get('x_passportattachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_passportattachment = base64.encodestring(FileData)
        if not post.get('x_passportattachment'):
           x_passportattachment = rtc.x_passportattachment
        if post.get('x_passportattachment_filename'):
           x_passportattachment_filename = post.get('x_passportattachment_filename')
        if not post.get('x_passportattachment_filename'):
           x_passportattachment_filename = rtc.x_passportattachment_filename
        if post.get('x_rfpe_attachment'):
           FileStorage = post.get('x_rfpe_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rfpe_attachment = base64.encodestring(FileData)
        if not post.get('x_rfpe_attachment'):
           x_rfpe_attachment = rtc.x_rfpe_attachment
        if post.get('x_rfpe_attachment_filename'):
           x_rfpe_attachment_filename = post.get('x_rfpe_attachment_filename')
        if not post.get('x_rfpe_attachment_filename'):
           x_rfpe_attachment_filename = rtc.x_rfpe_attachment_filename
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_passportno': post.get('x_passportno'),
                     'x_dob':post.get('x_dob'),
                     'x_rfpe_registration_valid_date':post.get('x_rfpe_registration_valid_date'),
                     'x_engineering_discipline':post.get('x_engineering_discipline'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_passportattachment':x_passportattachment,
                     'x_passportattachment_filename':x_passportattachment_filename,
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_passportexpiredate': post.get('x_passportexpiredate'),
                     'x_lcompany': post.get('x_lcompany'),
                     'x_gender': post.get('x_gender'),
                     'x_citizenship': post.get('x_citizenship'),
                     'x_rfpe_attachment': x_rfpe_attachment,
                     'x_rfpe_attachment_filename': post.get('x_rfpe_attachment_filename'),
                    }
           rtc.sudo().write(values)
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',13),('x_application_id','=',jobid)],limit=1)
           date =  fields.Datetime.now()
           val = {
                    'x_applicant_id': rtc.id,
                    'x_payment_status': 'Pending',
                    'x_application_payment_id': apay.id,
                    'x_apply_date': date,
                    'x_remark':'RFPE Renewal',
                    'x_job_id': rtc.job_id.id,
                    'x_partner_id': rtc.partner_id.id,
                  }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(val)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           payid = Pay.id
           payurl = durl+str(payid)
           message = "Your renewal form is renewed and please pay payment "+payurl
           subject = "Renew Application"
           useremail = old_data.email_from
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect(payurl)
           if not y["state"]:
              return request.redirect('/home')

    @http.route('/submit_rlperenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rlperenewalregistration(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        re_values = {
                   'x_applicant_id':old_data.id,
                   'x_job_id':old_data.job_id.id,
                   'x_approval_no': old_data.x_approval_no,
                   'x_reg_no': old_data.x_reg_no,
                   'x_name':old_data.partner_name,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_address_en':old_data.x_address_en,
                   'x_nrc1en':old_data.x_nrc1en,
                   'x_nrc2en':old_data.x_nrc2en,
                   'x_nrc3en':old_data.x_nrc3en,
                   'x_nrc4en':old_data.x_nrc4en,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_dob':old_data.x_dob,
                   #'x_pe_registration_valid_date':old_data.x_pe_registration_valid_date,
                   'x_firstdegree_engineer_discipline':old_data.x_firstdegree_engineer_discipline,
                   'x_firstdegree_graduation_year':old_data.x_firstdegree_graduation_year,
                   'x_partner_phone':old_data.partner_phone,
                   'x_email_from':old_data.email_from,
                   'x_passportattachment_filename':old_data.x_passportattachment_filename,
                   'x_passportattachment':old_data.x_passportattachment,
                   'x_photo':old_data.x_photo,
                   'x_renewal_date': todaydate,
                   'x_passportexpiredate': old_data.x_passportexpiredate,
                   'x_lcompany': old_data.x_lcompany,
                   'x_gender': old_data.x_gender,
                   'x_citizenship': old_data.x_citizenship,
                   'x_passportexpiredate': old_data.x_passportexpiredate,
                    }
        renwal_history = http.request.env['x_renewal_history'].sudo().create(re_values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': old_data.id, 'x_job_id': old_data.job_id.id}
        history.sudo().create(hvalue)
        renew_val = { 'x_user_id':old_data.partner_id.id, 'x_applicant_id': old_data.id, 'x_renewal_date': todaydate,'x_application_type':old_data.job_id.id,'x_reg_no': old_data.x_reg_no, 'x_approval_no': old_data.x_approval_no}
        renew = http.request.env['x_renewal'].sudo().create(renew_val)
        #id = post.get('id')
        rtc = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_passportattachment'):
           FileStorage = post.get('x_passportattachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_passportattachment = base64.encodestring(FileData)
        if not post.get('x_passportattachment'):
           x_passportattachment = rtc.x_passportattachment
        if post.get('x_passportattachment_filename'):
           x_passportattachment_filename = post.get('x_passportattachment_filename')
        if not post.get('x_passportattachment_filename'):
           x_passportattachment_filename = rtc.x_passportattachment_filename
        if post.get('x_rlpe_attachment'):
           FileStorage = post.get('x_rlpe_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rlpe_attachment = base64.encodestring(FileData)
        if not post.get('x_rlpe_attachment'):
           x_rlpe_attachment = rtc.x_rlpe_attachment
        if post.get('x_rlpe_attachment_filename'):
           x_rlpe_attachment_filename = post.get('x_rlpe_attachment_filename')
        if not post.get('x_rlpe_attachment_filename'):
           x_rlpe_attachment_filename = rtc.x_rlpe_attachment_filename
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_passportno':post.get('x_passportno'),
                     'x_dob':post.get('x_dob'),
                     'x_pe_registration_valid_date':post.get('x_pe_registration_valid_date'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_passportattachment':x_passportattachment,
                     'x_passportattachment_filename':x_passportattachment_filename,
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_passportexpiredate': post.get('x_passportexpiredate'),
                     'x_lcompany': post.get('x_lcompany'),
                     'x_gender': post.get('x_gender'),
                     'x_citizenship': post.get('x_citizenship'),
                     'x_rlpe_attachment': x_rlpe_attachment,
                     'x_rlpe_attachment_filename': post.get('x_rlpe_attachment_filename'),
                    }
           rtc.sudo().write(values)
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',13),('x_application_id','=',jobid)],limit=1)
           date =  fields.Datetime.now()
           val = {
                    'x_applicant_id': rtc.id,
                    'x_payment_status': 'Pending',
                    'x_application_payment_id': apay.id,
                    'x_apply_date': date,
                    'x_remark':'RLPE Renewal',
                    'x_job_id': rtc.job_id.id,
                    'x_partner_id': rtc.partner_id.id,
                  }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(val)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           payid = Pay.id
           payurl = durl+str(payid)
           message = "Your renewal form is renewed and please pay payment "+payurl
           subject = "Renew Application"
           useremail = old_data.email_from
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect(payurl)
           if not y["state"]:
              return request.redirect('/home')


    @http.route('/submit_recrenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_recrenewalregistration(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        re_values = {
                   'x_applicant_id':old_data.id,
                   'x_job_id':old_data.job_id.id,
                   'x_approval_no': old_data.x_approval_no,
                   'x_reg_no': old_data.x_reg_no,
                   'x_name':old_data.partner_name,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_address_en':old_data.x_address_en,
                   'x_nrc1en':old_data.x_nrc1en,
                   'x_nrc2en':old_data.x_nrc2en,
                   'x_nrc3en':old_data.x_nrc3en,
                   'x_nrc4en':old_data.x_nrc4en,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_dob':old_data.x_dob,
                   'x_rec_registration_valid_date':old_data.x_rec_registration_valid_date,
                   'x_firstdegree_engineer_discipline':old_data.x_firstdegree_engineer_discipline,
                   'x_firstdegree_graduation_year':old_data.x_firstdegree_graduation_year,
                   'x_partner_phone':old_data.partner_phone,
                   'x_email_from':old_data.email_from,
                   'x_nrc_photo_front_name':old_data.x_nrc_photo_front_name,
                   'x_nrc_photo_back_name':old_data.x_nrc_photo_back_name,
                   'x_nrc_photo_front':old_data.x_nrc_photo_front,
                   'x_nrc_photo_back':old_data.x_nrc_photo_back,
                   'x_photo':old_data.x_photo,
                   'x_renewal_date': todaydate,
                    }
        renwal_history = http.request.env['x_renewal_history'].sudo().create(re_values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': old_data.id, 'x_job_id': old_data.job_id.id}
        history.sudo().create(hvalue)
        renew_val = { 'x_user_id':old_data.partner_id.id, 'x_applicant_id': old_data.id, 'x_renewal_date': todaydate,'x_application_type':old_data.job_id.id,'x_reg_no': old_data.x_reg_no, 'x_approval_no': old_data.x_approval_no}
        renew = http.request.env['x_renewal'].sudo().create(renew_val)
        #id = post.get('id')
        rtc = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back= base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo       
        if post.get('x_rec_attachment'):
           FileStorage = post.get('x_rec_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
              return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rec_attachment = base64.encodestring(FileData)
        if not post.get('x_rec_attachment'):
           x_rec_attachment = rec.x_rec_attachment
        if post.get('x_rec_attachment_filename'):
           x_rec_attachment_filename = post.get('x_rec_attachment_filename')
        if not post.get('x_rec_attachment_filename'):
           x_rec_attachment_filename = rtc.x_rec_attachment_filename
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_rec_registration_valid_date':post.get('x_rec_registration_valid_date'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_rec_attachment': x_rec_attachment,
                     'x_rec_attachment_filename':x_rec_attachment_filename,
                    }
           rtc.sudo().write(values)
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',13),('x_application_id','=',jobid)],limit=1)
           date =  fields.Datetime.now()
           val = {
                    'x_applicant_id': rtc.id,
                    'x_payment_status': 'Pending',
                    'x_application_payment_id': apay.id,
                    'x_apply_date': date,
                    'x_remark':'REC Renewal',
                    'x_job_id': rtc.job_id.id,
                    'x_partner_id': rtc.partner_id.id,
                  }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(val)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           payid = Pay.id
           payurl = durl+str(payid)
           message = "Your renewal form is renewed and please pay payment "+payurl
           subject = "Renew Application"
           useremail = old_data.email_from
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect(payurl)
           if not y["state"]:
              return request.redirect('/home')



    @http.route('/submit_rsecrenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rsecrenewalregistration1(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        re_values = {
                   'x_applicant_id':old_data.id,
                   'x_job_id':old_data.job_id.id,
                   'x_approval_no': old_data.x_approval_no,
                   'x_reg_no': old_data.x_reg_no,
                   'x_name':old_data.partner_name,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_address_en':old_data.x_address_en,
                   'x_nrc1en':old_data.x_nrc1en,
                   'x_nrc2en':old_data.x_nrc2en,
                   'x_nrc3en':old_data.x_nrc3en,
                   'x_nrc4en':old_data.x_nrc4en,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_dob':old_data.x_dob,
                   'x_rsec_registration_valid_date':old_data.x_rsec_registration_valid_date,
                   'x_firstdegree_engineer_discipline':old_data.x_firstdegree_engineer_discipline,
                   'x_firstdegree_graduation_year':old_data.x_firstdegree_graduation_year,
                   'x_partner_phone':old_data.partner_phone,
                   'x_email_from':old_data.email_from,
                   'x_nrc_photo_front_name':old_data.x_nrc_photo_front_name,
                   'x_nrc_photo_back_name':old_data.x_nrc_photo_back_name,
                   'x_nrc_photo_front':old_data.x_nrc_photo_front,
                   'x_nrc_photo_back':old_data.x_nrc_photo_back,
                   'x_photo':old_data.x_photo,
                   'x_renewal_date': todaydate,
                    }
        renwal_history = http.request.env['x_renewal_history'].sudo().create(re_values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': old_data.id, 'x_job_id': old_data.job_id.id}
        history.sudo().create(hvalue)
        renew_val = { 'x_user_id':old_data.partner_id.id, 'x_applicant_id': old_data.id, 'x_renewal_date': todaydate,'x_application_type':old_data.job_id.id,'x_reg_no': old_data.x_reg_no, 'x_approval_no': old_data.x_approval_no}
        renew = http.request.env['x_renewal'].sudo().create(renew_val)
        #id = post.get('id')
        rtc = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back= base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if post.get('x_re_id'):
           FileStorage = post.get('x_re_id')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_re_id = base64.encodestring(FileData)
        if post.get('x_rsec_attachment'):
           FileStorage = post.get('x_rsec_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rsec_attachment = base64.encodestring(FileData)
        if not post.get('x_rsec_attachment'):
           x_rsec_attachment = rtc.x_rsec_attachment
        if post.get('x_rsec_attachment_filename'):
           x_rsec_attachment_filename = post.get('x_rsec_attachment_filename')
        if not post.get('x_rsec_attachment_filename'):
           x_rsec_attachment_filename = rtc.x_rsec_attachment_filename
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_rsec_registration_valid_date':post.get('x_rsec_registration_valid_date'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_re_id':x_re_id,
                     'x_re_id_name': post.get('x_re_id_name'),
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_rsec_attachment':x_rsec_attachment,
                     'x_rsec_attachment_filename': x_rsec_attachment_filename,
                    }
           rtc.sudo().write(values)
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',13),('x_application_id','=',jobid)],limit=1)
           date =  fields.Datetime.now()
           val = {
                    'x_applicant_id': rtc.id,
                    'x_payment_status': 'Pending',
                    'x_application_payment_id': apay.id,
                    'x_apply_date': date,
                    'x_remark':'RSEC Renewal',
                    'x_job_id': rtc.job_id.id,
                    'x_partner_id': rtc.partner_id.id,
                  }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(val)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           payid = Pay.id
           payurl = durl+str(payid)
           message = "Your renewal form is renewed and please pay payment "+payurl
           subject = "Renew Application"
           useremail = old_data.email_from
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect(payurl)
           if not y["state"]:
              return request.redirect('/home')


    @http.route('/submit_perenewalregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_perenewalregistration1(self, **post):
        userid = request.env.user.partner_id.id
        jjobid = post.get('jid')
        jobid = int(jjobid)
        todaydate =  fields.Datetime.now()
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        re_values = {
                   'x_applicant_id':old_data.id,
                   'x_job_id':old_data.job_id.id,
                   'x_approval_no': old_data.x_approval_no,
                   'x_reg_no': old_data.x_reg_no,
                   'x_name':old_data.partner_name,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_address_en':old_data.x_address_en,
                   'x_nrc1en':old_data.x_nrc1en,
                   'x_nrc2en':old_data.x_nrc2en,
                   'x_nrc3en':old_data.x_nrc3en,
                   'x_nrc4en':old_data.x_nrc4en,
                   'x_nrc_no_en':old_data.x_nrc_no_en,
                   'x_dob':old_data.x_dob,
                   'x_pe_registration_valid_date':old_data.x_pe_registration_valid_date,
                   'x_firstdegree_engineer_discipline':old_data.x_firstdegree_engineer_discipline,
                   'x_firstdegree_graduation_year':old_data.x_firstdegree_graduation_year,
                   'x_partner_phone':old_data.partner_phone,
                   'x_email_from':old_data.email_from,
                   'x_nrc_photo_front_name':old_data.x_nrc_photo_front_name,
                   'x_nrc_photo_back_name':old_data.x_nrc_photo_back_name,
                   'x_nrc_photo_front':old_data.x_nrc_photo_front,
                   'x_nrc_photo_back':old_data.x_nrc_photo_back,
                   'x_photo':old_data.x_photo,
                   'x_renewal_date': todaydate,
                    }
        renwal_history = http.request.env['x_renewal_history'].sudo().create(re_values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': old_data.id, 'x_job_id': old_data.job_id.id}
        history.sudo().create(hvalue)
        #rtcid = request.website._website_form_last_record().sudo().id
        renew_val = { 'x_user_id':old_data.partner_id.id, 'x_applicant_id': old_data.id, 'x_renewal_date': todaydate,'x_application_type':old_data.job_id.id,'x_reg_no': old_data.x_reg_no, 'x_approval_no': old_data.x_approval_no}
        renew = http.request.env['x_renewal'].sudo().create(renew_val)
        #id = post.get('id')
        rtc = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',old_data.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': old_data.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if post.get('x_re_id'):
           FileStorage = post.get('x_re_id')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_re_id = base64.encodestring(FileData)
        #if not post.get('x_re_id'):
           #x_cpd_status = rtc.x_cpd_status
        if post.get('x_pe_attachment'):
           FileStorage = post.get('x_pe_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_pe_attachment = base64.encodestring(FileData)
        if not post.get('x_pe_attachment'):
           x_pe_attachment = rtc.x_pe_attachment
        if post.get('x_pe_attachment_filename'):
           x_pe_attachment_filename = post.get('x_pe_attachment_filename')
        if not post.get('x_pe_attachment_filename'):
           x_pe_attachment_filename = rtc.x_pe_attachment_filename
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_pe_registration_valid_date':post.get('x_pe_registration_valid_date'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_re_id':x_re_id,
                     'x_re_id_name': post.get('x_re_id_name'),
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_pe_attachment': x_pe_attachment,
                     'x_pe_attachment_filename': x_pe_attachment_filename,
                    }
           rtc.sudo().write(values)
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',13),('x_application_id','=',jobid)],limit=1)
           date =  fields.Datetime.now()
           val = {
                    'x_applicant_id': rtc.id,
                    'x_payment_status': 'Pending',
                    'x_application_payment_id': apay.id,
                    'x_apply_date': date,
                    'x_remark':'PE Renewal',
                    'x_job_id': rtc.job_id.id,
                    'x_partner_id': rtc.partner_id.id,
                  }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(val)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           payid = Pay.id
           payurl = durl+str(payid)
           message = "Your renewal form is renewed and please pay payment "+payurl
           subject = "Renew Application"
           useremail = old_data.email_from
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect(payurl)
           if not y["state"]:
              return request.redirect('/home')

    @http.route(['/rtcregistrationform'], type='http', auth='public', website=True)
    def rtc_data(self, **kw):
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',3)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',3)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rtcregistrationform', {'nrc':nrc, 'ddata':ddata,'todaydate':todaydate,'lid':lid})

    @http.route('/save_rtcregistrationform', website=True, auth='public', method='POST')
    def save_rtcregistration(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.rtcregistrationform',{'academicfiles':academicfiles,'rtcdata':rtcdata,'ddata':ddata,'sresult':name,'nrc':nrc})


    @http.route('/submit_rtcregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rtcregistration1(self, **post):
        #rtcid = request.website._website_form_last_record().sudo().id
        id = post.get('id')
        date =  fields.Datetime.now()
        adate = date.date()
        rtc = request.env['hr.applicant'].sudo().search([('id','=',id)])
        dis = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        if dis:
            if post:
                res = 'no data'
                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    vals = {
                           'x_discipline':[(6, 0, val)]
                    }
                    value = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })

        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = rtc.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = rtc.x_other_attachment_name_1
        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = rtc.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = rtc.x_other_attachment_name_2
        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = rtc.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = rtc.x_other_attachment_name_3
        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = rtc.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = rtc.x_other_attachment_name_4
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        RTC = request.env['hr.applicant'].sudo().search([('id','=',id)])
        if RTC:
           values = {
                     'partner_name':post.get('partner_name'),
                     'x_reg_no':post.get('x_reg_no'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_address_en':post.get('x_address_en'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_experience_year':post.get('x_experience_year'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_academic_qualification':post.get('x_academic_qualification'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                    # 'x_firstdegree_attachment':x_firstdegree_attachment,
                    #'x_firstdegree_filename':x_firstdegree_filename,
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc1mm':post.get('x_nrc1mm'),
                     'x_nrc2mm':post.get('x_nrc2mm'),
                     'x_nrc3mm':post.get('x_nrc3mm'),
                     'x_nrc4mm':post.get('x_nrc4mm'),
                     'partner_id':post.get('partner_id'),
                     'x_state':4,
                     'x_form_status':4,
                     'x_discipline_s':post.get('x_discipline_s'),
                     'x_applied_date': adate,
                     'x_other_attachment_1':x_other_attachment_1,
                     'x_other_attachment_name_1':x_other_attachment_name_1,
                     'x_other_attachment_2':x_other_attachment_2,
                     'x_other_attachment_name_2':x_other_attachment_name_2,
                     'x_other_attachment_3':x_other_attachment_3,
                     'x_other_attachment_name_3':x_other_attachment_name_3,
                     'x_other_attachment_4':x_other_attachment_4,
                     'x_other_attachment_name_4':x_other_attachment_name_4,
                     'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                     'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                     'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                     'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                   }
           RTC.sudo().write(values)
          # RTC.sudo().write(value)
          # RTC.sudo().write(vals)
           type = 'RTC'
           hid = ' '+id+' '
           pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
           useremail = pdata1.email_from
           message = "Your registration for registered technician certificate with reg no RTC-"+hid+" has been summited"
           subject = "Submit Application"
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect('/my-record')
              #return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
           if not y["state"]:
              return request.redirect('/home')


    @http.route('/previousrtcregistration', website=True, auth='public', method='POST')
    def previous_rtc(self, **kw):
        id = kw.get('id')
        #rtcid = request.website._website_form_last_record().sudo().id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        type = 'RTC'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':rtcdata,'nrc':nrc,'ddata':ddata})

    def submit_rtc_details(self, details):
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())






    @http.route(['/rgtcregistrationform'], type='http', auth='public', website=True)
    def rgtc__data(self, **kw):
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          ddata = http.request.env['x_discipline'].sudo().search([])
          todaydate =  fields.Datetime.now()
          pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',4)])
          if pdata:
             lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',4)], order="id desc", limit=1)[0]
          if not pdata:
             lid = ' '
          return http.request.render('website.rgtcregistrationform', {'nrc':nrc,'ddata':ddata,'todaydate':todaydate,'lid':lid})

    @http.route('/save_rgtcregistrationform', website=True, auth='public', method='POST')
    def save_rgtcregistration(self, **kw):
        name = kw.get('name')
        if not name:
            name = 1
        rtcid = request.website._website_form_last_record().sudo().id
        rgtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        pcount = http.request.env['hr.applicant'].sudo().search_count([('id','=',rtcid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.rgtcregistrationform',{'rgtcdata':rgtcdata,'ddata':ddata,'sresult':name,'nrc':nrc,'academicfiles':academicfiles})


    @http.route('/submit_rgtcregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def submit_rgtcregistration1(self, **post):
        #rtcid = request.website._website_form_last_record().sudo().id
        id = post.get('id')
        date =  fields.Datetime.now()
        adate = date.date()
        rtc = request.env['hr.applicant'].sudo().search([('id','=',id)])
        dis = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value1 = {
                           'x_discipline':[(6, 0, val)]
                    }
                    value2 = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = rtc.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = rtc.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = rtc.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = rtc.x_nrc_photo_back_name


        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = rtc.x_photo
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = rtc.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = rtc.x_other_attachment_name_1


        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = rtc.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = rtc.x_other_attachment_name_2


        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = rtc.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = rtc.x_other_attachment_name_3

        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = rtc.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = rtc.x_other_attachment_name_4
        if rtc:
           values = {
                     'partner_name':post.get('partner_name'),
                     'x_reg_no':post.get('x_reg_no'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_address_en':post.get('x_address_en'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_experience_year':post.get('x_experience_year'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_academic_qualification':post.get('x_academic_qualification'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_photo':x_photo,
                     #'x_firstdegree_attachment':x_firstdegree_attachment,
                     #'x_firstdegree_filename':x_firstdegree_filename,
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc1mm':post.get('x_nrc1mm'),
                     'x_nrc2mm':post.get('x_nrc2mm'),
                     'x_nrc3mm':post.get('x_nrc3mm'),
                     'x_nrc4mm':post.get('x_nrc4mm'),
                     'partner_id':post.get('partner_id'),
                     'x_state':4,
                     'x_form_status':4,
                     'x_discipline_s':post.get('x_discipline_s'),
                     'x_applied_date': adate,
                     'x_other_attachment_1':x_other_attachment_1,
                     'x_other_attachment_name_1':x_other_attachment_name_1,
                     'x_other_attachment_2':x_other_attachment_2,
                     'x_other_attachment_name_2':x_other_attachment_name_2,
                     'x_other_attachment_3':x_other_attachment_3,
                     'x_other_attachment_name_3':x_other_attachment_name_3,
                     'x_other_attachment_4':x_other_attachment_4,
                     'x_other_attachment_name_4':x_other_attachment_name_4,
                     'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                     'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                     'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                     'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                  }
       # rtc.sudo().write(value2)
       # rtc.sudo().write(value1)
        rtc.sudo().write(values)
        type = 'RGTC'
        hid = ' '+id+' '
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for registered graduate technician certificate with reg no RGTC-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
           #return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
        if not y["state"]:
           return request.redirect('/home')




    @http.route('/reviewrgtcregistration', website=True, auth='public', method='POST')
    def previous_rgtc(self, **kw):
        #id = kw.get('applicant')
        ddata = http.request.env['x_discipline'].sudo().search([])
        rtcid =kw.get('id')
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',rtcid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        type = 'RGTC'
        return http.request.render('website.reviewregistrationform',{'type':type,'predata':rtcdata,'nrc':nrc,'ddata':ddata})

    @http.route(['/rsec-registration-form'], type='http', auth='public', website=True)
    def rsec_data(self, **kw):
          #pid = kw.get('id')
          #pe = request.website._website_form_last_record().sudo().id
          #pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          todaydate =  fields.Datetime.now()
          pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',5)])
          if pdata:
             lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',5)], order="id desc", limit=1)[0]
          if not pdata:
             lid = ' '
          return http.request.render('website.rsec-registration-form', {'nrc':nrc,'nrcmm':nrcmm,'lid':lid, 'todaydate':todaydate, 'ddata': ddata})

    @http.route(['/rsecregistrationformupdate'], type='http', auth='public', website=True)
    def rsecupdate_data(self, **kw):
          pid = kw.get('id')
          peid = request.website._website_form_last_record().sudo().id
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          ddata = http.request.env['x_discipline'].sudo().search([])
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
          return http.request.render('website.rsec-registration-form', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'ddata':ddata,'academicfiles':academicfiles,'anotherfiles':anotherfiles})

    @http.route('/previousrsec', type='http', auth='public', website=True, method='POST')
    def previous_rsec(self, **kw):
        pid = kw.get('id')
       # peid = request.website._website_form_last_record().sudo().id
        predata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        type = 'RSEC'
        return http.request.render('website.reviewregistrationform', {'type':type,'predata':predata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'anotherfiles':anotherfiles})

    @http.route(['/submit_rsecregistrationform'], type='http', auth='public', website=True, method=['POST'])
    def submit_rsec(self, **post):
        #  pid = kw.get('id')
        peid = post.get('id')
         # pe = request.website._website_form_last_record().sudo().id
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        dis = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        date =  fields.Datetime.now()
        adate = date.date()
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'4', 'x_applicant_id': peid, 'x_job_id': 5}
        history.sudo().create(hvalue)
        if post.get('x_discipline'):
           list_id = request.httprequest.form.getlist('x_discipline')
           count = 0
           val = []
           for mm in list_id:
               val.append(list_id[count])
               count = count + 1
               value = { 'x_discipline':[(6, 0, val)]}
               vals = { 'x_discipline':[(5,)] }
        if request.httprequest.method == 'POST':  
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_another' in request.params:
              attached_files = request.httprequest.files.getlist('x_another')
              import base64
              if attached_files:
                 anotherfiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  anotherfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_another',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })

        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = pdata.x_photo
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = pdata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = pdata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = pdata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = pdata.x_nrc_photo_back_name
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = pdata.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = pdata.x_other_attachment_name_1


        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = pdata.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = pdata.x_other_attachment_name_2


        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = pdata.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = pdata.x_other_attachment_name_3

        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = pdata.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = pdata.x_other_attachment_name_4
        Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        if Job:
           val = {
                    'x_state':4,
                    'x_reg_no':post.get('x_reg_no'),
                   # 'x_title':post.get('x_title'),
                    'x_dob':post.get('x_dob'),
                    'x_name_mm':post.get('x_name_mm'),
                    'x_father_en':post.get('x_father_en'),
                    'x_father_mm':post.get('x_father_mm'),
                    'x_nrc_no_en':post.get('x_nrc_no_en'),
                    'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                    'partner_name':post.get('partner_name'),
                    'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                    'x_address_en':post.get('x_address_en'),
                    'x_address_mm':post.get('x_address_mm'),
                    'partner_phone':post.get('partner_phone'),
                    'x_nrc_photo_front':x_nrc_photo_front,
                    'x_nrc_photo_front_name':x_nrc_photo_front_name,
                    'x_nrc_photo_back':x_nrc_photo_back,
                    'x_nrc_photo_back_name':x_nrc_photo_back_name,
                    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_nrc1en':post.get('x_nrc1en'),
                    'x_nrc2en':post.get('x_nrc2en'),
                    'x_nrc3en':post.get('x_nrc3en'),
                    'x_nrc4en':post.get('x_nrc4en'),
                    'x_nrc1mm':post.get('x_nrc1mm'),
                    'x_nrc2mm':post.get('x_nrc2mm'),
                    'x_nrc3mm':post.get('x_nrc3mm'),
                    'x_nrc4mm':post.get('x_nrc4mm'),
                    'x_form_status':4,
                    'x_discipline_s':post.get('x_discipline_s'),
                    'x_applied_date': adate,
                    'x_experience_year':post.get('x_experience_year'),
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                 }
        Job.sudo().write(val)
        if post.get('x_discipline'):
           Job.sudo().write(vals)
           Job.sudo().write(value)
       # academicfiles.sudo().write(x_academic)
        type = 'RSEC'
        hid = str(peid)
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for registered senior engineer certificate with reg no RSEC-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
          # return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
        if not y["state"]:
           return request.redirect('/home')


    @http.route(['/rlecregistrationformupdate'], type='http', auth='public', website=True)
    def rlec_updateform(self, **kw):
          pid = kw.get('id')
          pe = request.website._website_form_last_record().sudo().id
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pe)])
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pe),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pe),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.rleregistrationform', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'mpbiafiles':mpbiafiles})

    @http.route('/rlecregistrationformupdate1',type='http', auth="public", methods=['POST'], website=True)
    def rle_update(self, **post):
          peid = post.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          #nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
          date =  fields.Datetime.now()
          adate = date.date()
          history = http.request.env['x_history'].sudo().search([])
          hvalue = { 'x_state':'4', 'x_applicant_id': peid, 'x_job_id': 6}
          history.sudo().create(hvalue)
          if request.httprequest.method == 'POST':
             if 'x_academic' in request.params:
                attached_files = request.httprequest.files.getlist('x_academic')
                import base64
                if attached_files:
                   academicfiles.sudo().unlink()
                for attachment in attached_files:
                    FileExtension = attachment.filename.split('.')[-1].lower()
                    ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                    if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                       return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                    attached_file = attachment.read()
                    org_filename = attachment.filename
                    filename_without_extension = os.path.splitext(org_filename)[0]
                    #todaydate =  fields.Datetime.now()
                    datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                    random_number = str(randint(10000, 99999))
                    file_extension = pathlib.Path(org_filename).suffix
                    final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                    academicfiles.sudo().create({
                        #'name': attachment.filename,
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
               })
          if request.httprequest.method == 'POST':
             if 'x_mpbia' in request.params:
                attached_files = request.httprequest.files.getlist('x_mpbia')
                import base64
                if attached_files:
                   mpbiafiles.sudo().unlink()
                for attachment in attached_files:
                    FileExtension = attachment.filename.split('.')[-1].lower()
                    ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                    if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                       return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                    attached_file = attachment.read()
                    org_filename = attachment.filename
                    filename_without_extension = os.path.splitext(org_filename)[0]
                    #todaydate =  fields.Datetime.now()
                    datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                    random_number = str(randint(10000, 99999))
                    file_extension = pathlib.Path(org_filename).suffix
                    final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                    #attached_file = attachment.read()
                    mpbiafiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_mpbia',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
          if post.get('x_photo'):
             FileStorage = post.get('x_photo')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_photo = base64.encodestring(FileData)
          if not post.get('x_photo'):
             x_photo = pdata.x_photo
          if post.get('x_other_attachment_1'):
             FileStorage = post.get('x_other_attachment_1')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_1 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_1'):
             x_other_attachment_1 = pdata.x_other_attachment_1
          if post.get('x_other_attachment_name_1'):
             x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
          if not post.get('x_other_attachment_name_1'):
             x_other_attachment_name_1 = pdata.x_other_attachment_name_1
          if post.get('x_other_attachment_2'):
             FileStorage = post.get('x_other_attachment_2')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_2 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_2'):
             x_other_attachment_2 = pdata.x_other_attachment_2
          if post.get('x_other_attachment_name_2'):
             x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
          if not post.get('x_other_attachment_name_2'):
             x_other_attachment_name_2 = pdata.x_other_attachment_name_2
          if post.get('x_other_attachment_3'):
             FileStorage = post.get('x_other_attachment_3')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_3 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_3'):
             x_other_attachment_3 = pdata.x_other_attachment_3
          if post.get('x_other_attachment_name_3'):
             x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
          if not post.get('x_other_attachment_name_3'):
             x_other_attachment_name_3 = pdata.x_other_attachment_name_3
          if post.get('x_other_attachment_4'):
             FileStorage = post.get('x_other_attachment_4')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_4 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_4'):
             x_other_attachment_4 = pdata.x_other_attachment_4
          if post.get('x_other_attachment_name_4'):
             x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
          if not post.get('x_other_attachment_name_4'):
              x_other_attachment_name_4 = pdata.x_other_attachment_name_4
          if post.get('x_passportattachment'):
             FileStorage = post.get('x_passportattachment')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_passportattachment = base64.encodestring(FileData)
          if not post.get('x_passportattachment'):
             x_passportattachment = pdata.x_passportattachment
          if post.get('x_passportattachment_filename_update'):
             x_passportattachment_filename_update = post.get('x_passportattachment_filename_update')
          if not post.get('x_passportattachment_filename_update'):
             x_passportattachment_filename_update = pdata.x_passportattachment_filename_update
          Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          if Job:
             val = {
                    'x_state':4,
                    'x_reg_no':post.get('x_reg_no'),
                   # 'x_title':post.get('x_title'),
                    'partner_name':post.get('partner_name'),
                    'x_citizenship':post.get('x_citizenship'),
                    'x_dob':post.get('x_dob'),
                    'x_pob':post.get('x_pob'),
                    'x_passportno':post.get('x_passportno'),
                    'x_passportexpiredate':post.get('x_passportexpiredate'),
                    'x_passportplace':post.get('x_passportplace'),
                    'x_dateofissue':post.get('x_dateofissue'),
                    'x_dperno':post.get('x_dperno'),
                    'email_from':post.get('email_from'),
                    'partner_phone':post.get('partner_phone'),
                    'x_per_fax_no':post.get('x_per_fax_no'),
                    'x_address_en':post.get('x_address_en'),
                    'x_gender':post.get('x_gender'),
                    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_sfec':post.get('x_sfec'),
                    'x_lnre':post.get('x_lnre'),
                    'x_lrno':post.get('x_lrno'),
                    'x_ldesignation':post.get('x_ldesignation'),
                    'x_lcompany':post.get('x_lcompany'),
                    'x_laddress':post.get('x_laddress'),
                    'x_lemail':post.get('x_lemail'),
                    'x_ltelno':post.get('x_ltelno'),
                    'x_lfaxno':post.get('x_lfaxno'),
                    'x_passportattachment_filename_update':x_passportattachment_filename_update,
                    'x_passportattachment':x_passportattachment,
                    'x_passport_name':post.get('x_passport_name'),
                    'x_academic_qualification':post.get('x_academic_qualification'),
                    'x_form_status':4,
                    'x_applied_date': adate,
                    'x_mpbi':post.get('x_mpbi'),
                    #'x_mpbiattachment':x_mpbiattachment,
                    #'x_mpbiattachment_filename':x_mpbiattachment_filename,
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                 }
             Job.sudo().write(val)
             #Job.sudo().write(vals)
             #Job.sudo().write(value)
             type = 'RLE'
             hid = str(peid)
             pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
             useremail = pdata1.email_from
             message = "Your registration for apprentice engineer certificate with reg no RLE-"+hid+" has been summited"
             subject = "Submit Application"
             y = send_email(useremail,message,subject)
             if y["state"]:
                return http.request.redirect('/my-record')
               # return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
             if not y["state"]:
               return request.redirect('/home')

    #@http.route('/rlecregistrationformupdate1',type='http', auth="public", methods=['POST'], website=True)
    #def rlecupdate(self, **post):
    #      pid = post.get('id')
    #      pe = request.website._website_form_last_record().sudo().id
    #      pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pe)])
    #      nrc = http.request.env['x_nrclist'].sudo().search([],)
    #      nrcmm = http.request.env['x_nrclist'].sudo().search([],)
    #      #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
    #      if post.get('x_other_attachments'):
    #         FileStorage = post.get('x_other_attachments')
    #         FileExtension = FileStorage.filename.split('.')[-1].lower()
    #         ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
    #         if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
    #             return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
    #         import base64
    #         FileData = FileStorage.read()
    #         x_other_attachments = base64.encodestring(FileData)
    #      if not post.get('x_other_attachments'):
    #         x_other_attachments = pdata.x_other_attachments
    #      if post.get('x_other_attachments_filename'):
    #         x_other_attachments_filename = post.get('x_other_attachments_filename')
    #      if not post.get('x_other_attachments_filename'):
    #         x_other_attachments_filename = pdata.x_other_attachments_filename
    #      if post.get('x_mpbiattachment'):
    #         FileStorage = post.get('x_mpbiattachment')
    #         FileExtension = FileStorage.filename.split('.')[-1].lower()
    #         ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
    #         if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
    #             return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
    #         import base64
    #         FileData = FileStorage.read()
    #         x_mpbiattachment = base64.encodestring(FileData)
    #      if not post.get('x_mpbiattachment'):
    #         x_mpbiattachment = pdata.x_mpbiattachment
    #      if post.get('x_mpbiattachment_filename'):
    #         x_mpbiattachment_filename = post.get('x_mpbiattachment_filename')
    #      if not post.get('x_mpbiattachment_filename'):
    #         x_mpbiattachment_filename = pdata.x_mpbiattachment_filename
    #      if post.get('x_passportattachment'):
    #         FileStorage = post.get('x_passportattachment')
    #         FileExtension = FileStorage.filename.split('.')[-1].lower()
    #         ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
    #         if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
    #             return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
    #         import base64
    #         FileData = FileStorage.read()
    #         x_passportattachment = base64.encodestring(FileData)
    #      if not post.get('x_passportattachment'):
    #         x_passportattachment = pdata.x_passportattachment
    #      if post.get('x_passportattachment_filename'):
    #         x_passportattachment_filename = post.get('x_passportattachment_filename')
    #      if not post.get('x_passportattachment_filename'):
    #         x_passportattachment_filename = pdata.x_passportattachment_filename
    #      if post.get('x_dprattachment'):
    #         FileStorage = post.get('x_dprattachment')
    #         FileExtension = FileStorage.filename.split('.')[-1].lower()
    #         ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
    #         if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
    #             return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
    #         import base64
    #         FileData = FileStorage.read()
    #         x_dprattachment = base64.encodestring(FileData)
    #      if not post.get('x_dprattachment'):
    #         x_dprattachment = pdata.x_dprattachment
    #      if post.get('x_dprattachment_filename'):
    #         x_dprattachment_filename = post.get('x_dprattachment_filename')
    #      if not post.get('x_dprattachment_filename'):
    #         x_dprattachment_filename = pdata.x_dprattachment_filename
    #      rle = request.env['hr.applicant'].sudo().search([('id','=',pid)])
    #      if rle:
    #       values = {
    #                 'x_reg_no':post.get('x_reg_no'),
    #                 'x_gender':post.get('x_gender'),
    #                 'partner_name':post.get('partner_name'),
    #                 'x_citizenship':post.get('x_citizenship'),
    #                 'x_dob':post.get('x_dob'),
    #                 'x_pob':post.get('x_pob'),
    #                 'x_passportno':post.get('x_passportno'),
    #                 'x_passportexpiredate':post.get('x_passportexpiredate'),
    #                 'x_passportplace':post.get('x_passportplace'),
    #                 'x_dateofissue':post.get('x_dateofissue'),
    #                 'x_dperno':post.get('x_dperno'),
    #                 'email_from':post.get('email_from'),
    #                # 'x_per_email':post.get('x_per_email'),
    #                 'x_address_en':post.get('x_address_en'),
    #                 'partner_phone':post.get('partner_phone'),
    #                # 'x_per_tel_no':post.get('x_per_tel_no'),
    #                 'x_per_fax_no':post.get('x_per_fax_no'),
    #                 'x_mpbi':post.get('x_mpbi'),
    #                 'x_mpbiattachment':x_mpbiattachment,
    #                 'x_mpbiattachment_filename':x_mpbiattachment_filename,
    #                 'x_sfec':post.get('x_sfec'),
    #                 'x_lnre':post.get('x_lnre'),
    #                 'x_lrno':post.get('x_lrno'),
    #                 'x_ldesignation':post.get('x_ldesignation'),
    #                 'x_lcompany':post.get('x_lcompany'),
    #                 'x_laddress':post.get('x_laddress'),
    #                 'x_lemail':post.get('x_lemail'),
    #                 'x_ltelno':post.get('x_ltelno'),
    #                 'x_lfaxno':post.get('x_lfaxno'),
    #                 'x_dprattachment':x_dprattachment,
    #                 'x_dprattachment_filename':x_dprattachment_filename,
    #                 'x_other_attachments':x_other_attachments,
    #                 'x_other_attachments_filename':x_other_attachments_filename,
    #                 'x_passportattachment':x_passportattachment,
    #                 'x_passportattachment_filename':x_passportattachment_filename,
    #                 'x_state':2,
    #                }
    #       rle.sudo().write(values)
    #       type = 'RLE'
    #      return http.request.render('website_hr_recruitment.thankyou', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'type':type})


    #@http.route(['/rlecregistrationformupdate'], type='http', methods=['POST'], auth='public', website=True)
    #def rleupdate_data(self, **post):
          #pid = kw.get('id')
          #pe = request.website._website_form_last_record().sudo().id
          #pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          #Job = request.env['hr.applicant'].sudo().search([('id','=',pid)])
          #if rle:
           #values = {
                     #'x_reg_no':post.get('x_reg_no'),
                     #'x_gender':post.get('x_gender'),
                     #'partner_name':post.get('partner_name'),
                     #'x_citizenship':post.get('x_citizenship'),
                     #'x_dob':post.get('x_dob'),
                     #'x_dop':post.get('x_dop'),
                     #'x_passportno':post.get('x_passportno'),
                     #'x_passportexpiredate':post.get('x_passportexpiredate'),
                     #'x_passportplace':post.get('x_passportplace'),
                     #'x_dateofissue':post.get('x_dateofissue'),
                     #'x_dperno':post.get('x_dperno'),
                     #'email_form':post.get('email_form'),
                     #'x_address_en':post.get('x_address_en'),
                     #'parter_phone':post.get('parter_phone'),
                     #'x_per_fax_no':post.get('x_per_fax_no'),
                     #'x_mpbi':post.get('x_mpbi'),
                     #'x_mpbiattachment':post.get('x_mpbiattachment'),
                     #'x_sfec':post.get('x_sfec'),
                     #'x_lnre':post.get('x_lnre'),
                     #'x_lrno':post.get('x_lrno'),
                     #'x_ldesignation':post.get('x_ldesignation'),
                     #'x_lcompany':post.get('x_lcompany'),
                     #'x_laddress':post.get('x_laddress'),
                     #'x_lemail':post.get('x_lemail'),
                     #'x_ltelno':post.get('x_ltelno'),
                     #'x_lfaxno':post.get('x_lfaxno'),
                     #'x_dprattachment':post.get('x_dprattachment'),
                     #'x_other_attachments':post.get('x_other_attachments'),
                     #'x_passportattachment':post.get('x_passportattachment'),
                    #}
        #rle.sudo().write(values)
        #return http.request.render('website.rlecregistrationformupdate', {'pdata':pdata})



    @http.route(['/rlperegistrationformupdate'], type='http', auth='public', website=True)
    def rspeupdate_data(self, **kw):
          pid = kw.get('id')
          pe = request.website._website_form_last_record().sudo().id
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pe)])
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pe),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pe),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.rlperegistrationform', {'pdata':pdata,'mpbiafiles':mpbiafiles,'academicfiles':academicfiles,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/rlperegistrationformupdate1',type='http', auth="public", methods=['POST'], website=True)
    def rlpe_update(self, **post):
          peid = post.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          #nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
          date =  fields.Datetime.now()
          adate = date.date()
          history = http.request.env['x_history'].sudo().search([])
          hvalue = { 'x_state':'4', 'x_applicant_id': peid, 'x_job_id': 7}
          history.sudo().create(hvalue)
          if request.httprequest.method == 'POST':
             if 'x_academic' in request.params:
                attached_files = request.httprequest.files.getlist('x_academic')
                import base64
                if attached_files:
                   academicfiles.sudo().unlink()
                for attachment in attached_files:
                    FileExtension = attachment.filename.split('.')[-1].lower()
                    ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                    if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                       return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                    attached_file = attachment.read()
                    org_filename = attachment.filename
                    filename_without_extension = os.path.splitext(org_filename)[0]
                    #todaydate =  fields.Datetime.now()
                    datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                    random_number = str(randint(10000, 99999))
                    file_extension = pathlib.Path(org_filename).suffix
                    final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                    academicfiles.sudo().create({
                        #'name': attachment.filename,
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
	  					 })
          if request.httprequest.method == 'POST':
             if 'x_mpbia' in request.params:
                attached_files = request.httprequest.files.getlist('x_mpbia')
                import base64
                if attached_files:
                   mpbiafiles.sudo().unlink()
                for attachment in attached_files:
                    FileExtension = attachment.filename.split('.')[-1].lower()
                    ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                    if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                       return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                    attached_file = attachment.read()
                    org_filename = attachment.filename
                    filename_without_extension = os.path.splitext(org_filename)[0]
                    #todaydate =  fields.Datetime.now()
                    datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                    random_number = str(randint(10000, 99999))
                    file_extension = pathlib.Path(org_filename).suffix
                    final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                    #attached_file = attachment.read()
                    mpbiafiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_mpbia',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
          if post.get('x_photo'):
             FileStorage = post.get('x_photo')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_photo = base64.encodestring(FileData)
          if not post.get('x_photo'):
             x_photo = pdata.x_photo
          if post.get('x_other_attachment_1'):
             FileStorage = post.get('x_other_attachment_1')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_1 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_1'):
             x_other_attachment_1 = pdata.x_other_attachment_1
          if post.get('x_other_attachment_name_1'):
             x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
          if not post.get('x_other_attachment_name_1'):
             x_other_attachment_name_1 = pdata.x_other_attachment_name_1
          if post.get('x_other_attachment_2'):
             FileStorage = post.get('x_other_attachment_2')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_2 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_2'):
             x_other_attachment_2 = pdata.x_other_attachment_2
          if post.get('x_other_attachment_name_2'):
             x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
          if not post.get('x_other_attachment_name_2'):
             x_other_attachment_name_2 = pdata.x_other_attachment_name_2
          if post.get('x_other_attachment_3'):
             FileStorage = post.get('x_other_attachment_3')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_3 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_3'):
             x_other_attachment_3 = pdata.x_other_attachment_3
          if post.get('x_other_attachment_name_3'):
             x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
          if not post.get('x_other_attachment_name_3'):
             x_other_attachment_name_3 = pdata.x_other_attachment_name_3
          if post.get('x_other_attachment_4'):
             FileStorage = post.get('x_other_attachment_4')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_4 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_4'):
             x_other_attachment_4 = pdata.x_other_attachment_4
          if post.get('x_other_attachment_name_4'):
             x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
          if not post.get('x_other_attachment_name_4'):
              x_other_attachment_name_4 = pdata.x_other_attachment_name_4
          if post.get('x_passportattachment'):
             FileStorage = post.get('x_passportattachment')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_passportattachment = base64.encodestring(FileData)
          if not post.get('x_passportattachment'):
             x_passportattachment = pdata.x_passportattachment
          if post.get('x_passportattachment_filename_update'):
             x_passportattachment_filename_update = post.get('x_passportattachment_filename_update')
          if not post.get('x_passportattachment_filename_update'):
             x_passportattachment_filename_update = pdata.x_passportattachment_filename_update
          Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          if Job:
             val = {
                    'x_state':4,
                    'x_reg_no':post.get('x_reg_no'),
                   # 'x_title':post.get('x_title'),
                    'partner_name':post.get('partner_name'),
                    'x_citizenship':post.get('x_citizenship'),
                    'x_dob':post.get('x_dob'),
                    'x_pob':post.get('x_pob'),
	 	    'x_passportno':post.get('x_passportno'),
	 	    'x_passportexpiredate':post.get('x_passportexpiredate'),
	 	    'x_passportplace':post.get('x_passportplace'),
	 	    'x_dateofissue':post.get('x_dateofissue'),
	 	    'x_dperno':post.get('x_dperno'),
	 	    'email_from':post.get('email_from'),
                    'partner_phone':post.get('partner_phone'),
	 	    'x_per_fax_no':post.get('x_per_fax_no'),
	 	    'x_address_en':post.get('x_address_en'),
                    'x_gender':post.get('x_gender'),
	 	    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_sfec':post.get('x_sfec'),
	 	    'x_lnre':post.get('x_lnre'),
	 	    'x_lrno':post.get('x_lrno'),
	 	    'x_ldesignation':post.get('x_ldesignation'),
	 	    'x_lcompany':post.get('x_lcompany'),
	 	    'x_laddress':post.get('x_laddress'),
	 	    'x_lemail':post.get('x_lemail'),
	 	    'x_ltelno':post.get('x_ltelno'),
	 	    'x_lfaxno':post.get('x_lfaxno'),
	 	    'x_passportattachment_filename_update':x_passportattachment_filename_update,
                    'x_passportattachment':x_passportattachment,
	 	    'x_passport_name':post.get('x_passport_name'),
                    'x_academic_qualification':post.get('x_academic_qualification'),
                    'x_form_status':4,
	 	    'x_applied_date': adate,
	            'x_mpbi':post.get('x_mpbi'),
                    #'x_mpbiattachment':x_mpbiattachment,
                    #'x_mpbiattachment_filename':x_mpbiattachment_filename,
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                 }
             Job.sudo().write(val)
             #Job.sudo().write(vals)
             #Job.sudo().write(value)
             type = 'RLPE'
             hid = str(peid)
             pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
             useremail = pdata1.email_from
             message = "Your registration for apprentice engineer certificate with reg no RLPE-"+hid+" has been summited"
             subject = "Submit Application"
             y = send_email(useremail,message,subject)
             if y["state"]:
                return http.request.redirect('/my-record')
               # return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
             if not y["state"]:
               return request.redirect('/home')

    @http.route(['/rfperegistrationformupdate'], type='http', auth='public', website=True)
    def rfpecupdate_data(self, **kw):
          pid = kw.get('id')
          pe = request.website._website_form_last_record().sudo().id
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pe)])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pe),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pe),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.rfperegistrationform', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'mpbiafiles':mpbiafiles})

    @http.route('/rfperegistrationformupdate1',type='http', auth="public", methods=['POST'], website=True)
    def rfpe_update(self, **post):
          pid = post.get('id')
          #pe = request.website._website_form_last_record().sudo().id
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
          mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&','&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
          if request.httprequest.method == 'POST':
             if 'x_academic' in request.params:
                attached_files = request.httprequest.files.getlist('x_academic')
                import base64
                if attached_files:
                   academicfiles.sudo().unlink()
                for attachment in attached_files:
                    attached_file = attachment.read()
                    org_filename = attachment.filename
                    filename_without_extension = os.path.splitext(org_filename)[0]
                    #todaydate =  fields.Datetime.now()
                    datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                    random_number = str(randint(10000, 99999))
                    file_extension = pathlib.Path(org_filename).suffix
                    final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                    academicfiles.sudo().create({
                          'name': final_filename,
                          'res_model': 'hr.applicant',
                          'res_id': pid,
                          'type': 'binary',
                          'x_field': 'x_academic',
                          'public':'true',
                          'datas': base64.encodestring(attached_file),
                      })
          if request.httprequest.method == 'POST':
             if 'x_mpbia' in request.params:
                attached_files = request.httprequest.files.getlist('x_mpbia')
                import base64
                if attached_files:
                   mpbiafiles.sudo().unlink()
                for attachment in attached_files:
                    attached_file = attachment.read()
                    org_filename = attachment.filename
                    filename_without_extension = os.path.splitext(org_filename)[0]
                    #todaydate =  fields.Datetime.now()
                    datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                    random_number = str(randint(10000, 99999))
                    file_extension = pathlib.Path(org_filename).suffix
                    final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                    mpbiafiles.sudo().create({
                          'name': final_filename,
                          'res_model': 'hr.applicant',
                          'res_id': pid,
                          'type': 'binary',
                          'x_field': 'x_mpbia',
                          'public':'true',
                          'datas': base64.encodestring(attached_file),
                      })
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          if post.get('x_photo'):
             FileStorage = post.get('x_photo')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                 return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_photo = base64.encodestring(FileData)
          if not post.get('x_photo'):
             x_photo = pdata.x_photo

          if post.get('x_other_attachment_1'):
             FileStorage = post.get('x_other_attachment_1')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                 return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_1 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_1'):
             x_other_attachment_1 = pdata.x_other_attachment_1
          if post.get('x_other_attachment_name_1'):
             x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
          if not post.get('x_other_attachment_name_1'):
             x_other_attachment_name_1 = pdata.x_other_attachment_name_1


          if post.get('x_other_attachment_2'):
             FileStorage = post.get('x_other_attachment_2')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                 return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_2 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_2'):
             x_other_attachment_2 = pdata.x_other_attachment_2
          if post.get('x_other_attachment_name_2'):
             x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
          if not post.get('x_other_attachment_name_2'):
             x_other_attachment_name_2 = pdata.x_other_attachment_name_2


          if post.get('x_other_attachment_3'):
             FileStorage = post.get('x_other_attachment_3')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                 return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_3 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_3'):
             x_other_attachment_3 = pdata.x_other_attachment_3
          if post.get('x_other_attachment_name_3'):
             x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
          if not post.get('x_other_attachment_name_3'):
             x_other_attachment_name_3 = pdata.x_other_attachment_name_3

          if post.get('x_other_attachment_4'):
             FileStorage = post.get('x_other_attachment_4')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                 return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_other_attachment_4 = base64.encodestring(FileData)
          if not post.get('x_other_attachment_4'):
             x_other_attachment_4 = pdata.x_other_attachment_4
          if post.get('x_other_attachment_name_4'):
             x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
          if not post.get('x_other_attachment_name_4'):
             x_other_attachment_name_4 = pdata.x_other_attachment_name_4

          if post.get('x_passportattachment'):
             FileStorage = post.get('x_passportattachment')
             FileExtension = FileStorage.filename.split('.')[-1].lower()
             ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
             if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                 return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
             import base64
             FileData = FileStorage.read()
             x_passportattachment = base64.encodestring(FileData)
          if not post.get('x_passportattachment'):
             x_passportattachment = pdata.x_passportattachment
          if post.get('x_passportattachment_filename_update'):
             x_passportattachment_filename_update = post.get('x_passportattachment_filename_update')
          if not post.get('x_passportattachment_filename_update'):
             x_passportattachment_filename_update = pdata.x_passportattachment_filename_update
          rfpe = request.env['hr.applicant'].sudo().search([('id','=',pid)])
          if rfpe:
           values = {
                     'x_state':4,
                     'x_form_status':4,
                     'x_reg_no':post.get('x_reg_no'),
                     'x_gender':post.get('x_gender'),
                     'partner_name':post.get('partner_name'),
                     'x_citizenship':post.get('x_citizenship'),
                     'x_dob':post.get('x_dob'),
                     'x_pob':post.get('x_pob'),
                     'x_passportno':post.get('x_passportno'),
                     'x_passportexpiredate':post.get('x_passportexpiredate'),
                     'x_passportplace':post.get('x_passportplace'),
                     'x_dateofissue':post.get('x_dateofissue'),
                     'x_dperno':post.get('x_dperno'),
                     'email_from':post.get('email_from'),
                    # 'x_per_email':post.get('x_per_email'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                    # 'x_per_tel_no':post.get('x_per_tel_no'),
                     'x_per_fax_no':post.get('x_per_fax_no'),
                     'x_mpbi':post.get('x_mpbi'),
                     'x_sfec':post.get('x_sfec'),
                     'x_lnre':post.get('x_lnre'),
                     'x_lrno':post.get('x_lrno'),
                     'x_ldesignation':post.get('x_ldesignation'),
                     'x_lcompany':post.get('x_lcompany'),
                     'x_laddress':post.get('x_laddress'),
                     'x_lemail':post.get('x_lemail'),
                     'x_ltelno':post.get('x_ltelno'),
                     'x_lfaxno':post.get('x_lfaxno'),
                     'x_other_attachment_1':x_other_attachment_1,
                     'x_other_attachment_name_1':x_other_attachment_name_1,
                     'x_other_attachment_2':x_other_attachment_2,
                     'x_other_attachment_name_2':x_other_attachment_name_2,
                     'x_other_attachment_3':x_other_attachment_3,
                     'x_other_attachment_name_3':x_other_attachment_name_3,
                     'x_other_attachment_4':x_other_attachment_4,
                     'x_other_attachment_name_4':x_other_attachment_name_4,
                     'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                     'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                     'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                     'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                     'x_passportattachment':x_passportattachment,
                     'x_passportattachment_filename_update':x_passportattachment_filename_update,
                     'x_acperegno':post.get('x_acperegno'),
                    }
           rfpe.sudo().write(values)
           type = 'RFPE'
           hid = str(pid)
           pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
           useremail = pdata1.email_from
           message = "Your registration for apprentice engineer certificate with reg no RFPE-"+hid+" has been summited"
           subject = "Submit Application"
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect('/my-record')
             # return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
           if not y["state"]:
              return request.redirect('/home')

class QueryURL(object):
    def __init__(self, path='', path_args=None, **args):
        self.path = path
        self.args = args
        self.path_args = OrderedSet(path_args or [])

    def __call__(self, path=None, path_args=None, **kw):
        path = path or self.path
        for key, value in self.args.items():
            kw.setdefault(key, value)
        path_args = OrderedSet(path_args or []) | self.path_args
        paths, fragments = {}, []
        for key, value in kw.items():
            if value and key in path_args:
                if isinstance(value, models.BaseModel):
                    paths[key] = slug(value)
                else:
                    paths[key] = u"%s" % value
            elif value:
                if isinstance(value, list) or isinstance(value, set):
                    fragments.append(werkzeug.url_encode([(key, item) for item in value]))
                else:
                    fragments.append(werkzeug.url_encode([(key, value)]))
        for key in path_args:
            value = paths.get(key)
            if value is not None:
                path += '/' + key + '/' + value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path


class Website(Home):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        homepage = request.website.homepage_id
        if homepage and (homepage.sudo().is_visible or request.env.user.has_group('base.group_user')) and homepage.url != '/':
            return request.env['ir.http'].reroute(homepage.url)

        website_page = request.env['ir.http']._serve_page()
        if website_page:
            return website_page
        else:
            top_menu = request.website.menu_id
            first_menu = top_menu and top_menu.child_id and top_menu.child_id.filtered(lambda menu: menu.is_visible)
            if first_menu and first_menu[0].url not in ('/', '', '#') and (not (first_menu[0].url.startswith(('/?', '/#', ' ')))):
                return request.redirect(first_menu[0].url)

        raise request.not_found()

    @http.route('/website/force_website', type='json', auth="user")
    def force_website(self, website_id):
        request.env['website']._force_website(website_id)
        return True

    # ------------------------------------------------------
    # Login - overwrite of the web login so that regular users are redirected to the backend
    # while portal users are redirected to the frontend by default
    # ------------------------------------------------------

    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                redirect = b'/web?' + request.httprequest.query_string
            else:
                redirect = '/my'
            return http.redirect_with_hash(redirect)
        return response

    # ------------------------------------------------------
    # Business
    # ------------------------------------------------------

    @http.route('/website/get_languages', type='json', auth="user", website=True)
    def website_languages(self, **kwargs):
        return [(lg.code, lg.url_code, lg.name) for lg in request.website.language_ids]

    @http.route('/website/lang/<lang>', type='http', auth="public", website=True, multilang=False)
    def change_lang(self, lang, r='/', **kwargs):
        """ :param lang: supposed to be value of `url_code` field """
        if lang == 'default':
            lang = request.website.default_lang_id.url_code
            r = '/%s%s' % (lang, r or '/')
        redirect = werkzeug.utils.redirect(r or ('/%s' % lang), 303)
        lang_code = request.env['res.lang']._lang_get_code(lang)
        redirect.set_cookie('frontend_lang', lang_code)
        return redirect

    @http.route(['/website/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def country_infos(self, country, **kw):
        fields = country.get_address_fields()
        return dict(fields=fields, states=[(st.id, st.name, st.code) for st in country.state_ids], phone_code=country.phone_code)

    @http.route(['/robots.txt'], type='http', auth="public")
    def robots(self, **kwargs):
        return request.render('website.robots', {'url_root': request.httprequest.url_root}, mimetype='text/plain')

    @http.route('/sitemap.xml', type='http', auth="public", website=True, multilang=False, sitemap=False)
    def sitemap_xml_index(self, **kwargs):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        View = request.env['ir.ui.view'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None

        def create_sitemap(url, content):
            return Attachment.create({
                'datas': base64.b64encode(content),
                'mimetype': mimetype,
                'type': 'binary',
                'name': url,
                'url': url,
            })
        dom = [('url', '=', '/sitemap-%d.xml' % current_website.id), ('type', '=', 'binary')]
        sitemap = Attachment.search(dom, limit=1)
        if sitemap:
            # Check if stored version is still valid
            create_date = fields.Datetime.from_string(sitemap.create_date)
            delta = datetime.datetime.now() - create_date
            if delta < SITEMAP_CACHE_TIME:
                content = base64.b64decode(sitemap.datas)

        if not content:
            # Remove all sitemaps in ir.attachments as we're going to regenerated them
            dom = [('type', '=', 'binary'), '|', ('url', '=like', '/sitemap-%d-%%.xml' % current_website.id),
                   ('url', '=', '/sitemap-%d.xml' % current_website.id)]
            sitemaps = Attachment.search(dom)
            sitemaps.unlink()

            pages = 0
            locs = request.website.with_user(request.website.user_id).enumerate_pages()
            while True:
                values = {
                    'locs': islice(locs, 0, LOC_PER_SITEMAP),
                    'url_root': request.httprequest.url_root[:-1],
                }
                urls = View.render_template('website.sitemap_locs', values)
                if urls.strip():
                    content = View.render_template('website.sitemap_xml', {'content': urls})
                    pages += 1
                    last_sitemap = create_sitemap('/sitemap-%d-%d.xml' % (current_website.id, pages), content)
                else:
                    break

            if not pages:
                return request.not_found()
            elif pages == 1:
                # rename the -id-page.xml => -id.xml
                last_sitemap.write({
                    'url': "/sitemap-%d.xml" % current_website.id,
                    'name': "/sitemap-%d.xml" % current_website.id,
                })
            else:
                # TODO: in master/saas-15, move current_website_id in template directly
                pages_with_website = ["%d-%d" % (current_website.id, p) for p in range(1, pages + 1)]

                # Sitemaps must be split in several smaller files with a sitemap index
                content = View.render_template('website.sitemap_index_xml', {
                    'pages': pages_with_website,
                    'url_root': request.httprequest.url_root,
                })
                create_sitemap('/sitemap-%d.xml' % current_website.id, content)

        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route('/website/info', type='http', auth="public", website=True)
    def website_info(self, **kwargs):
        try:
            request.website.get_template('website.website_info').name
        except Exception as e:
            return request.env['ir.http']._handle_exception(e, 404)
        Module = request.env['ir.module.module'].sudo()
        apps = Module.search([('state', '=', 'installed'), ('application', '=', True)])
        l10n = Module.search([('state', '=', 'installed'), ('name', '=like', 'l10n_%')])
        values = {
            'apps': apps,
            'l10n': l10n,
            'version': odoo.service.common.exp_version()
        }
        return request.render('website.website_info', values)

    # ------------------------------------------------------
    # Edit
    # ------------------------------------------------------

    @http.route(['/website/pages', '/website/pages/page/<int:page>'], type='http', auth="user", website=True)
    def pages_management(self, page=1, sortby='url', search='', **kw):
        # only website_designer should access the page Management
        if not request.env.user.has_group('website.group_website_designer'):
            raise werkzeug.exceptions.NotFound()

        Page = request.env['website.page']
        searchbar_sortings = {
            'url': {'label': _('Sort by Url'), 'order': 'url'},
            'name': {'label': _('Sort by Name'), 'order': 'name'},
        }
        # default sortby order
        sort_order = searchbar_sortings.get(sortby, 'url')['order'] + ', website_id desc, id'

        domain = request.website.website_domain()
        if search:
            domain += ['|', ('name', 'ilike', search), ('url', 'ilike', search)]

        pages = Page.search(domain, order=sort_order)
        if sortby != 'url' or not request.env.user.has_group('website.group_multi_website'):
            pages = pages.filtered(pages._is_most_specific_page)
        pages_count = len(pages)

        step = 50
        pager = portal_pager(
            url="/website/pages",
            url_args={'sortby': sortby},
            total=pages_count,
            page=page,
            step=step
        )

        pages = pages[(page - 1) * step:page * step]

        values = {
            'pager': pager,
            'pages': pages,
            'search': search,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
        }
        return request.render("website.list_website_pages", values)

    @http.route(['/website/add/', '/website/add/<path:path>'], type='http', auth="user", website=True)
    def pagenew(self, path="", noredirect=False, add_menu=False, template=False, **kwargs):
        # for supported mimetype, get correct default template
        _, ext = os.path.splitext(path)
        ext_special_case = ext and ext in _guess_mimetype() and ext != '.html'

        if not template and ext_special_case:
            default_templ = 'website.default_%s' % ext.lstrip('.')
            if request.env.ref(default_templ, False):
                template = default_templ

        template = template and dict(template=template) or {}
        page = request.env['website'].new_page(path, add_menu=add_menu, **template)
        url = page['url']
        if noredirect:
            return werkzeug.wrappers.Response(url, mimetype='text/plain')

        if ext_special_case:  # redirect non html pages to backend to edit
            return werkzeug.utils.redirect('/web#id=' + str(page.get('view_id')) + '&view_type=form&model=ir.ui.view')
        return werkzeug.utils.redirect(url + "?enable_editor=1")

    @http.route("/website/get_switchable_related_views", type="json", auth="user", website=True)
    def get_switchable_related_views(self, key):
        views = request.env["ir.ui.view"].get_related_views(key, bundles=False).filtered(lambda v: v.customize_show)
        views = views.sorted(key=lambda v: (v.inherit_id.id, v.name))
        return views.read(['name', 'id', 'key', 'xml_id', 'arch', 'active', 'inherit_id'])

    @http.route('/website/toggle_switchable_view', type='json', auth='user', website=True)
    def toggle_switchable_view(self, view_key):
        request.website.viewref(view_key).toggle()

    @http.route('/website/reset_template', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def reset_template(self, view_id, mode='soft', redirect='/', **kwargs):
        """ This method will try to reset a broken view.
        Given the mode, the view can either be:
        - Soft reset: restore to previous architeture.
        - Hard reset: it will read the original `arch` from the XML file if the
        view comes from an XML file (arch_fs).
        """
        view = request.env['ir.ui.view'].browse(int(view_id))
        # Deactivate COW to not fix a generic view by creating a specific
        view.with_context(website_id=None).reset_arch(mode)
        return request.redirect(redirect)

    @http.route(['/website/publish'], type='json', auth="user", website=True)
    def publish(self, id, object):
        Model = request.env[object]
        record = Model.browse(int(id))

        values = {}
        if 'website_published' in Model._fields:
            values['website_published'] = not record.website_published
        record.write(values)
        return bool(record.website_published)

    @http.route(['/website/seo_suggest'], type='json', auth="user", website=True)
    def seo_suggest(self, keywords=None, lang=None):
        language = lang.split("_")
        url = "http://google.com/complete/search"
        try:
            req = requests.get(url, params={
                'ie': 'utf8', 'oe': 'utf8', 'output': 'toolbar', 'q': keywords, 'hl': language[0], 'gl': language[1]})
            req.raise_for_status()
            response = req.content
        except IOError:
            return []
        xmlroot = ET.fromstring(response)
        return json.dumps([sugg[0].attrib['data'] for sugg in xmlroot if len(sugg) and sugg[0].attrib['data']])

    # ------------------------------------------------------
    # Themes
    # ------------------------------------------------------

    def _get_customize_views(self, xml_ids):
        View = request.env["ir.ui.view"].with_context(active_test=False)
        if not xml_ids:
            return View
        domain = [("key", "in", xml_ids)] + request.website.website_domain()
        return View.search(domain).filter_duplicate()

    @http.route(['/website/theme_customize_get'], type='json', auth="public", website=True)
    def theme_customize_get(self, xml_ids):
        views = self._get_customize_views(xml_ids)
        return {
            'enabled': views.filtered('active').mapped('key'),
            'names': {view.key: view.name for view in views},
        }

    @http.route(['/website/theme_customize'], type='json', auth="public", website=True)
    def theme_customize(self, enable=None, disable=None, get_bundle=False):
        """ enable or Disable lists of ``xml_id`` of the inherit templates """

        self._get_customize_views(disable).write({'active': False})
        self._get_customize_views(enable).write({'active': True})

        if get_bundle:
            context = dict(request.context)
            return {
                'web.assets_common': request.env['ir.qweb']._get_asset_link_urls('web.assets_common', options=context),
                'web.assets_frontend': request.env['ir.qweb']._get_asset_link_urls('web.assets_frontend', options=context),
                'website.assets_editor': request.env['ir.qweb']._get_asset_link_urls('website.assets_editor', options=context),
            }

        return True

    @http.route(['/website/theme_customize_reload'], type='http', auth="public", website=True)
    def theme_customize_reload(self, href, enable, disable, tab=0, **kwargs):
        self.theme_customize(enable and enable.split(",") or [], disable and disable.split(",") or [])
        return request.redirect(href + ("&theme=true" if "#" in href else "#theme=true") + ("&tab=" + tab))

    @http.route(['/website/make_scss_custo'], type='json', auth='user', website=True)
    def make_scss_custo(self, url, values):
        """
        Params:
            url (str):
                the URL of the scss file to customize (supposed to be a variable
                file which will appear in the assets_common bundle)

            values (dict):
                key,value mapping to integrate in the file's map (containing the
                word hook). If a key is already in the file's map, its value is
                overridden.

        Returns:
            boolean
        """
        request.env['web_editor.assets'].make_scss_customization(url, values)
        return True

    @http.route(['/website/multi_render'], type='json', auth="public", website=True)
    def multi_render(self, ids_or_xml_ids, values=None):
        View = request.env['ir.ui.view']
        res = {}
        for id_or_xml_id in ids_or_xml_ids:
            res[id_or_xml_id] = View.render_template(id_or_xml_id, values)
        return res

    @http.route(['/website/update_visitor_timezone'], type='json', auth="public", website=True)
    def update_visitor_timezone(self, timezone):
        visitor_sudo = request.env['website.visitor']._get_visitor_from_request()
        if visitor_sudo:
            if timezone in pytz.all_timezones:
                visitor_sudo.write({'timezone': timezone})
                return True
        return False

    # ------------------------------------------------------
    # Server actions
    # ------------------------------------------------------

    @http.route([
        '/website/action/<path_or_xml_id_or_id>',
        '/website/action/<path_or_xml_id_or_id>/<path:path>',
    ], type='http', auth="public", website=True)
    def actions_server(self, path_or_xml_id_or_id, **post):
        ServerActions = request.env['ir.actions.server']
        action = action_id = None

        # find the action_id: either an xml_id, the path, or an ID
        if isinstance(path_or_xml_id_or_id, str) and '.' in path_or_xml_id_or_id:
            action = request.env.ref(path_or_xml_id_or_id, raise_if_not_found=False)
        if not action:
            action = ServerActions.search([('website_path', '=', path_or_xml_id_or_id), ('website_published', '=', True)], limit=1)
        if not action:
            try:
                action_id = int(path_or_xml_id_or_id)
            except ValueError:
                pass

        # check it effectively exists
        if action_id:
            action = ServerActions.browse(action_id).exists()
        # run it, return only if we got a Response object
        if action:
            if action.state == 'code' and action.website_published:
                action_res = action.run()
                if isinstance(action_res, werkzeug.wrappers.Response):
                    return action_res

        return request.redirect('/')


# ------------------------------------------------------
# Retrocompatibility routes
# ------------------------------------------------------
class WebsiteBinary(http.Controller):

    @http.route([
        '/website/image',
        '/website/image/<xmlid>',
        '/website/image/<xmlid>/<int:width>x<int:height>',
        '/website/image/<xmlid>/<field>',
        '/website/image/<xmlid>/<field>/<int:width>x<int:height>',
        '/website/image/<model>/<id>/<field>',
        '/website/image/<model>/<id>/<field>/<int:width>x<int:height>'
    ], type='http', auth="public", website=False, multilang=False)
    def content_image(self, id=None, max_width=0, max_height=0, **kw):
        if max_width:
            kw['width'] = max_width
        if max_height:
            kw['height'] = max_height
        if id:
            id, _, unique = id.partition('_')
            kw['id'] = int(id)
            if unique:
                kw['unique'] = unique
        return Binary().content_image(**kw)

    @http.route(['/favicon.ico'], type='http', auth='public', website=True, multilang=False, sitemap=False)
    def favicon(self, **kw):
        # when opening a pdf in chrome, chrome tries to open the default favicon url
        return self.content_image(model='website', id=str(request.website.id), field='favicon', **kw)




    @http.route('/home', auth='public', website=True)
    def testingblog(self, **kw):
        tblog = http.request.env['blog.post'].sudo().search([], limit=4)
        return http.request.render('website.homepage', {
        'tblog': tblog})

    @http.route('/testing', auth='public', website=True)
    def testingstate(self, **kw):
        st = http.request.env['x_state'].sudo().search([])
        township = http.request.env['x_township'].sudo().search([])
        my_stid = 1
        return http.request.render('website.testing', {'st': st, 'township': township, 'my_stid':my_stid})

    @http.route('/test2', auth='public', website=True)
    def testing2state(self, **kw):
        st = http.request.env['x_state'].sudo().search([])
        township = http.request.env['x_township'].sudo().search([])
        return http.request.render('website.test2', {'st': st, 'township': township})

    @http.route(['/accreditation','/accreditation/page/<int:page>'], type='http', auth='public', website=True)
    def accrediation_cate(self, page=1):
          accre = http.request.env['ir.attachment'].sudo().search([('x_category','=','Accreditation')],offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','Accreditation')])
          pager = request.website.pager(
               url='/accreditation',
               total=total,
               page=page,
               step=6,
               scope=4,
          )
          return http.request.render('website.accreditation', {'accre': accre,'pager':pager})

    @http.route(['/disciplinary-committee','/disciplinary-committee/page/<int:page>'], type='http', auth='public', website=True)
    def disciplinary_committee(self, page=1):
          disciplinary = http.request.env['ir.attachment'].sudo().search([('x_category','=','DisciplinaryCommittee')],offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','DisciplinaryCommittee')])
          pager = request.website.pager(
               url='/disciplinary-committee',
               total=total,
               page=page,
               step=6,
               scope=4,
          )
          return http.request.render('website.disciplinary-committee', {'disciplinary': disciplinary,'pager':pager})

    @http.route(['/national-and-international-relations-committee-nir','/national-and-international-relations-committee-nir/page/<int:page>'], type='http', auth='public', website=True)
    def nir_committee(self, page=1):
          nirc = http.request.env['ir.attachment'].sudo().search([('x_category','=','NIRC')],offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','NIRC')])
          pager = request.website.pager(
               url='/national-and-international-relations-committee-nir',
               total=total,
               page=page,
               step=6,
               scope=4,
          )
          return http.request.render('website.national-and-international-relations-committee-nir', {'nirc': nirc,'pager':pager})

    @http.route(['/standard-committee','/standard-committee/page/<int:page>'], type='http', auth='public', website=True)
    def standard_committee(self, page=1):
          stan = http.request.env['ir.attachment'].sudo().search([('x_category','=','SSC')],offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','SSC')])
          pager = request.website.pager(
               url='/standard-committee',
               total=total,
               page=page,
               step=6,
               scope=4,
          )
          return http.request.render('website.standard-committee', {'stan': stan,'pager':pager})

    @http.route(['/laws-regulation','/laws-regulation/page/<int:page>'], type='http', auth='public', website=True)
    def laws_display(self, page=1):
          laws = http.request.env['ir.attachment'].sudo().search([('x_category','=','LawsRegulation')],order="write_date asc" ,offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','LawsRegulation')])
          pager = request.website.pager(
               url='/laws-regulation',
               total=total,
               page=page,
               step=6,
               scope=3,
          )
          return http.request.render('website.laws-regulation', {'laws': laws,'pager':pager})


    @http.route(['/announcement','/announcement/page/<int:page>'], type='http', auth='public', website=True)
    def annoucement_display(self, page=1):
          annouce = http.request.env['ir.attachment'].sudo().search([('x_category','=','Announcement')],offset=(page-1) * 9, limit=9)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','Announcement')])
          pager = request.website.pager(
               url='/announcement',
               total=total,
               page=page,
               step=9,
               scope=4,
          )
          return http.request.render('website.announcement', {'annouce': annouce,'pager':pager})

    @http.route(['/guidelines','/guidelines/page/<int:page>'], type='http', auth='public', website=True)
    def guidelines_display(self, page=1):
          guide = http.request.env['ir.attachment'].sudo().search([('x_category','=','Guidelines')],order="write_date asc" ,offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','Guidelines')])
          pager = request.website.pager(
               url='/guidelines',
               total=total,
               page=page,
               step=6,
               scope=3,
          )
          return http.request.render('website.guidelines', {'guide': guide,'pager':pager})

    @http.route(['/continuing-profession-development-committee-cpd','/continuing-profession-development-committee-cpd/page/<int:page>'], type='http', auth='public', website=True)
    def cpdc_display(self, page=1):
          cpdc = http.request.env['ir.attachment'].sudo().search([('x_category','=','CPDCommittee')],order="write_date asc" ,offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','CPDCommittee')])
          pager = request.website.pager(
               url='/continuing-profession-development-committee-cpd',
               total=total,
               page=page,
               step=6,
               scope=3,
          )
          return http.request.render('website.continuing-professional-development-committee', {'cpdc': cpdc,'pager':pager})

    @http.route(['/ethics-committee','/ethics-committee/page/<int:page>'], type='http', auth='public', website=True)
    def ethics_display(self, page=1):
          ethic = http.request.env['ir.attachment'].sudo().search([('x_category','=','EthicsCommittee')],order="write_date asc" ,offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','EthicsCommittee')])
          pager = request.website.pager(
               url='/ethics-committee',
               total=total,
               page=page,
               step=6,
               scope=3,
          )
          return http.request.render('website.ethics-committee', {'ethic': ethic,'pager':pager})

    @http.route(['/sop-and-manual','/sop-and-manual/page/<int:page>'], type='http', auth='public', website=True)
    def sop_display(self, page=1):
          sop = http.request.env['ir.attachment'].sudo().search([('x_category','=','SOP')],order="write_date asc" ,offset=(page-1) * 6, limit=6)
          total = http.request.env['ir.attachment'].sudo().search_count([('x_category','=','SOP')])
          pager = request.website.pager(
               url='/sop-and-manual',
               total=total,
               page=page,
               step=6,
               scope=3,
          )
          return http.request.render('website.sop-and-manual', {'sop': sop,'pager':pager})


    @http.route(['/design','/design/page/<int:page>'], type='http', auth='public', website=True)
    def navigate_to_company_page(self, page=1):
       # This will get all company details (in case of multicompany this are multiple records)
       company = http.request.env['blog.post'].sudo().search([], offset=(page-1) * 20, limit=20)
       total = http.request.env['blog.post'].sudo().search_count([])
       now = fields.Datetime.now().date()
       pager = request.website.pager(
            url='/design',
            total=total,
            page=page,
            step=20,
            scope=7,
       )
       return http.request.render('website.design', {'company': company, 'pager': pager, 'now':now})# pass company details to the webpage in a variable



    @http.route(['/searchresults/','/searchresults/page/<int:page>/'],type='http', auth='public', website=True)
    def get_cart_vals(self, page=1,**kw):
          # YOUR VARIABLE value_input SHOULD BE AVAILABLE IN THE QUERY STRING
          #query_string = request.httprequest.query_string
          now = fields.Datetime.now().date()
          name = kw.get('name')
          name_lower = kw.get('name').lower()
          name_upper =kw.get('name').upper()
          com_name = http.request.env['blog.post'].sudo().search([])
          if com_name:
              res = http.request.env['blog.post'].sudo().search(['|','|','|',('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['blog.post'].sudo().search_count(['|','|','|',('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name)])
              #query = "select * from blog.post where name LIKE '%name%'"
              #request.cr.execute(query)
              #res = request.cr.fetchall()
              pager = request.website.pager(
                   url='/searchresults',
                   url_args= kw,
                   total=total,
                   page=page,
                   step=20,
                   scope=7,
              )
              if res:
                  return http.request.render('website.searchresults', {
                  # pass company details to the webpage in a variable
                  'name': res,'pager': pager,'now':now,'sresult':name})

              if not res:
                  a = ()
                  return http.request.render('website.searchresults', {
                  # pass company details to the webpage in a variable
                  'name': a,'sresult':name})

    @http.route(['/list-of-professional-engineers-pe','/list-of-professional-engineers-pe/page/<int:page>'], type='http', auth='public', website=True)
    def pelist(self, page=1):
          pe = http.request.env['x_list'].sudo().search([('x_type','=','PE')] ,offset=(page-1) * 30, limit=30)
          total = http.request.env['x_list'].sudo().search_count([])
          pager = request.website.pager(
               url='/list-of-professional-engineers-pe',
               total=total,
               page=page,
               step=30,
               scope=7,
          )
          return http.request.render('website.list-of-professional-engineers-pe', {'pe': pe,'pager':pager})


    @http.route(['/list-of-pe/','/list-of-pe/page/<int:page>/'],type='http', auth='public', website=True)
    def pe_list(self, page=1,**kw):
          # YOUR VARIABLE value_input SHOULD BE AVAILABLE IN THE QUERY STRING
          #query_string = request.httprequest.query_string
          now = fields.Datetime.now().date()
          name = kw.get('name')
          name_lower = kw.get('name').lower()
          name_upper =kw.get('name').upper()
          com_name = http.request.env['x_list'].sudo().search([])
          if com_name:
              res = http.request.env['x_list'].sudo().search(['|','|','|','|','|','|','|',('x_name','like',name),('x_name','like',name_lower),('x_name','like',name_upper),('x_name','ilike',name),('x_register_no','like',name),('x_register_no','like',name_lower),('x_register_no','like',name_upper),('x_register_no','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['x_list'].sudo().search_count(['|','|','|','|','|','|','|',('x_name','like',name),('x_name','like',name_lower),('x_name','like',name_upper),('x_name','ilike',name),('x_register_no','like',name),('x_register_no','like',name_lower),('x_register_no','like',name_upper),('x_register_no','ilike',name)])
              #query = "select * from blog.post where name LIKE '%name%'"
              #request.cr.execute(query)
              #res = request.cr.fetchall()
              pager = request.website.pager(
                   url='/list-of-pe',
                   url_args= kw,
                   total=total,
                   page=page,
                   step=20,
                   scope=7,
              )
              if res:
                  return http.request.render('website.list-of-pe', {
                  # pass company details to the webpage in a variable
                  'name': res,'pager': pager,'now':now,'sresult':name})

              if not res:
                  a = ()
                  return http.request.render('website.list-of-pe', {
                  # pass company details to the webpage in a variable
                  'name': a,'sresult':name})
   


    @http.route('/job1/', type='http', auth="public", methods=['POST'], website=True)
    def job_confirm(self, **post):
       job_datas = self._process_job_details(post)
       Job = request.env['x_proexperience']
       for job_data in job_datas:
           Job += Job.sudo().create(job_data)
       return request.redirect('/peinvolvement')

    def _process_job_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route('/involve/', type='http', auth="public", methods=['POST'], website=True)
    def involve_confirm(self, **post):
       involve_datas = self._process_involve_details(post)
       Involve = request.env['x_involve']
       for involve_data in involve_datas:
           Involve += Involve.sudo().create(involve_data)
       return request.redirect('/pesummary')

    def _process_involve_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route('/save_summary/', type='http', auth="public", methods=['POST'], website=True)
    def summary_confirm(self, **post):
       x_name = post.get('1-x_name')
       x_position = post.get('1-x_position')
       x_month = post.get('1-x_month')
       x_verifier_name = post.get('1-x_verifier_name')
       x_project = post.get('1-x_project')
       if x_name or x_position or x_month or x_verifier_name or x_project:
          summary_datas = self._process_summary_details(post)
          Summary = request.env['x_summary']
          for summary_data in summary_datas:
              Summary += Summary.sudo().create(summary_data)
       name = 1
       pe = post.get('1-x_applicant')
       peid = int(pe)
       if not peid:
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
          peid = pe.id
       pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
       pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
       return http.request.render('website.peverify',{'sresult':name,'peid':peid,'pedata':pedata,'pdata':pdata,'regsave':1})

    def _process_summary_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route('/verify1/', type='http', auth="public", methods=['POST'], website=True)
    def verify_confirm(self, **post):
       verify_datas = self._process_verify_details(post)
       Verifier = request.env['x_verify']
       pe = request.website._website_form_last_record().sudo().id
       update_info = request.env['hr.applicant'].sudo().search([('id','=',pe)])
       val = {'x_state':2}
       update_info.sudo().write(val)
       for verify_data in verify_datas:
           Verifier += Verifier.sudo().create(verify_data)
       return request.redirect('/job-thank-you')

    def _process_verify_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())



    @http.route(['/list-of-professional-engineering-pe','/list-of-professional-engineering-pe/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def peeng_list(self, page=1, **post):
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if not pename and not disid:
             res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
             total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1)])
             pager = request.website.pager(
                    url='/list-of-professional-engineering-pe',
                    total=total,
                    page=page,
                    step=10,
                    scope=7,
             )
             return http.request.render('website.list-of-professional-engineering-pe', {'res': res,'pager':pager,'disci':disci})
          if pename and disid:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
             disciplineid=int(disid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',1),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',1),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             pager = request.website.pager(
                  url='/list-of-professional-engineering-pe',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-professional-engineering-pe', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid})
          if not pename and disid:
             disciplineid=int(disid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',1),('x_discipline','=',disciplineid)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',1),('x_discipline','=',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-professional-engineering-pe',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-professional-engineering-pe', {'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid})

    @http.route(['/list-of-registered-senior-engineers-rse','/list-of-registered-senior-engineers-rse/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def rseeng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',5)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',5),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',5),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-registered-senior-engineers-rse',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-registered-senior-engineers-rse', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-registered-senior-engineers-rse',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-registered-senior-engineers-rse', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-registered-engineers-re','/list-of-registered-engineers-re/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def re_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',10)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',10),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',10),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-registered-engineers-re',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-registered-engineers-re', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-registered-engineers-re',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-registered-engineers-re', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-registered-graduate-technicians-rgtech','/list-of-registered-graduate-technicians-rgtech/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def rgtech_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',4)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',4),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',4),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-registered-graduate-technicians-rgtech',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-registered-graduate-technicians-rgtech', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-registered-graduate-technicians-rgtech',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-registered-graduate-technicians-rgtech', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-apprentice-graduate-technicians-agtech','/list-of-apprentice-graduate-technicians-agtech/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def agtech_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',12),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',12),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-apprentice-graduate-technicians-agtech',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-apprentice-graduate-technicians-agtech', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-apprentice-graduate-technicians-agtech',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-apprentice-graduate-technicians-agtech', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-apprentice-technicians-atech','/list-of-apprentice-technicians-atech/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def atech_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',11)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',11),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',11),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-apprentice-technicians-atech',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-apprentice-technicians-atech', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-apprentice-technicians-atech',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-apprentice-technicians-atech', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-asean-chartered-professional-engineers-acpe','/list-of-asean-chartered-professional-engineers-acpe/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def acpe_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',2),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',2),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-asean-chartered-professional-engineers-acpe',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-asean-chartered-professional-engineers-acpe', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-asean-chartered-professional-engineers-acpe',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-asean-chartered-professional-engineers-acpe', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-registered-limited-engineers-rle','/list-of-registered-limited-engineers-rle/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def rle_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',6)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',6),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',6),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-registered-limited-engineers-rle',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-registered-limited-engineers-rle', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-registered-limited-engineers-rle',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-registered-limited-engineers-rle', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-registered-limited-professional-engineers-rlpe','/list-of-registered-limited-professional-engineers-rlpe/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def rlpe_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',7)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',7),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',7),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-registered-limited-professional-engineers-rlpe',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-registered-limited-professional-engineers-rlpe', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-registered-limited-professional-engineers-rlpe',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-registered-limited-professional-engineers-rlpe', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-registered-foreign-professional-engineers-rfpe','/list-of-registered-foreign-professional-engineers-rfpe/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def rfpe_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',8)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',8),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',8),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-registered-foreign-professional-engineers-rfpe',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-registered-foreign-professional-engineers-rfpe', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-registered-foreign-professional-engineers-rfpe',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-registered-foreign-professional-engineers-rfpe', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})

    @http.route(['/list-of-pe2/','/list-of-pe2/page/<int:page>/'],type='http', auth='public', website=True)
    def peresult_list2(self, page=1,**kw):
          # YOUR VARIABLE value_input SHOULD BE AVAILABLE IN THE QUERY STRING
          #query_string = request.httprequest.query_string
          now = fields.Datetime.now().date()
          name = kw.get('name')
          name_lower = kw.get('name').lower()
          name_upper =kw.get('name').upper()
          com_name = http.request.env['hr.applicant'].sudo().search([])
    #xdesid = x_hr_applicant_x_discipline_rel.x_discipline_id;
    #xdes = http.request.env[' x_discipline'].sudo().search([('id','=',xdesid)])
          if com_name:
              res = http.request.env['hr.applicant'].sudo().search(['|','|','|',('partner_name','like',name),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['|','|','|',('partner_name','like',name),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',name)])
              #query = "select * from blog.post where name LIKE '%name%'"
              #request.cr.execute(query)
              #res = request.cr.fetchall()
              pager = request.website.pager(
                   url='/list-of-pe',
                   url_args= kw,
                   total=total,
                   page=page,
                   step=20,
                   scope=7,
              )
              if res:
                  return http.request.render('website.list-of-pe2', {
                  # pass company details to the webpage in a variable
                  'name': res,'pager': pager,'now':now,'sresult':name})

              if not res:
                  a = ()
                  return http.request.render('website.list-of-pe2', {
                  # pass company details to the webpage in a variable
                  'name': a,'sresult':name})

    @http.route(['/list-of-apprentice-engineers-ae','/list-of-apprentice-engineers-ae/page/<int:page>'], type='http', method=['POST'], auth='public', website=True)
    def ae_eng_list(self, page=1, **post):
          pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',9)] ,order="id desc"  ,offset=(page-1) * 10, limit=10)
          disid = post.get('disname')
          pename = post.get('pename')
          regno = post.get('regno')
          jjid = post.get('jid')
          disci = http.request.env['x_discipline'].sudo().search([])
          if regno:
             reg_no= int(regno)
          if not regno:
             reg_no= ' '
          if pename:
             name_lower = post.get('pename').lower()
             name_upper = post.get('pename').upper()
          if not pename:
             name_lower = ' '
             name_upper = ' '
          if disid:
             disciplineid=int(disid)
          if not disid:
             disciplineid= ' '
          if pename:
             jid = int(jjid)
             res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',9),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)],offset=(page-1) * 20, limit=20)
             total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',9),('x_discipline','=',disciplineid),'|','|','|','|',('x_reg_no','ilike',pename),('partner_name','like',pename),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',pename)])
             #res = http.request.env['hr.applicant'].sudo().search([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename),('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)],offset=(page-1) * 22, limit=22)
             #total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',1),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',pename),('x_reg_no','ilike',pename),('name','like',pename),('name','like',name_lower),('name','like',name_upper),('name','ilike',pename),('id','like',pename) ,('email_from','like',pename),('email_from','like',name_lower),('email_from','like',name_upper),('x_discipline.id','like',disciplineid)])
             pager = request.website.pager(
                  url='/list-of-apprentice-engineers-ae',
                  url_args= post,
                  total=total,
                  page=page,
                  step=20,
                  scope=5,
             )
             return http.request.render('website.list-of-apprentice-engineers-ae', {'pename':pename,'disid':disid,'disci':disci,'res':res,'pager':pager,'disciplineid':disciplineid,'jid':jid})
          if not pename:
             #disci = http.request.env['x_discipline'].sudo().search([])
             testdis=http.request.env['x_discipline'].sudo().search([('id','=',2)])
             total = http.request.env['hr.applicant'].sudo().search_count([])
             pager = request.website.pager(
                  url='/list-of-apprentice-engineers-ae',
                  total=total,
                  page=page,
                  step=10,
                  scope=7,
             )
             return http.request.render('website.list-of-apprentice-engineers-ae', {'pe': pe,'pager':pager,'testdis':testdis, 'disci': disci})


    @http.route(['/list-of-registered-technician-certificate','/list-of-registered-technician-certificate/page/<int:page>'], type='http', auth='public', website=True)
    def acpeeng_list(self, page=1):
          pe = http.request.env['hr.applicant'].sudo().search([] ,order="id asc"  ,offset=(page-1) * 10, limit=10)
          testdis=http.request.env['x_discipline'].sudo().search([('id','=',3)])
          total = http.request.env['hr.applicant'].sudo().search_count([])
          pager = request.website.pager(
               url='/list-of-registered-technician-certificate',
               total=total,
               page=page,
               step=10,
               scope=7,
          )
          return http.request.render('website.list-of-registered-technician-certificate', {'pe': pe,'pager':pager,'testdis':testdis})

    @http.route(['/list-of-rtc/','/list-of-rtc/page/<int:page>/'],type='http', auth='public', website=True)
    def rtc_result(self, page=1,**kw):
          # YOUR VARIABLE value_input SHOULD BE AVAILABLE IN THE QUERY STRING
          #query_string = request.httprequest.query_string
          now = fields.Datetime.now().date()
          name = kw.get('name')
          name_lower = kw.get('name').lower()
          name_upper =kw.get('name').upper()
          com_name = http.request.env['hr.applicant'].sudo().search([])
          #xdesid = x_hr_applicant_x_discipline_rel.x_discipline_id;
          #xdes = http.request.env[' x_discipline'].sudo().search([('id','=',xdesid)])
          if com_name:
              res = http.request.env['hr.applicant'].sudo().search(['|','|','|',('partner_name','like',name),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['|','|','|',('partner_name','like',name),('partner_name','like',name_lower),('partner_name','like',name_upper),('partner_name','ilike',name)])
              #query = "select * from blog.post where name LIKE '%name%'"
              #request.cr.execute(query)
              #res = request.cr.fetchall()
              pager = request.website.pager(
                   url='/list-of-rtc',
                   url_args= kw,
                   total=total,
                   page=page,
                   step=20,
                   scope=7,
              )
              if res:
                  return http.request.render('website.list-of-rtc', {
                  # pass company details to the webpage in a variable
                  'name': res,'pager': pager,'now':now,'sresult':name})
              if not res:
                  a = ()
                  return http.request.render('website.list-of-rtc', {
                  # pass company details to the webpage in a variable
                  'name': a,'sresult':name})  

    @http.route('/peregistrationupdate1', type='http', auth="public", methods=['POST'], website=True)
    def peregistration_update1(self, **post):
       # pe = request.website._website_form_last_record().sudo().id
        peid = post.get('id')
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        dis = http.request.env['x_discipline'].sudo().search([])
        careerfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_career')])
        programfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_program')])
        postdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_postdegree_attachment')])
        firstdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_firstdegree_attachment')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value = {
                           'x_discipline':[(6, 0, val)]
                    }
                    vals = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_career' in request.params:
              attached_files = request.httprequest.files.getlist('x_career')
              import base64
              if attached_files:
                 careerfiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  careerfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_career',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_program' in request.params:
              attached_files = request.httprequest.files.getlist('x_program')
              import base64
              if attached_files:
                 programfiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  programfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_program',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_firstdegree_attachment' in request.params:
              attached_files = request.httprequest.files.getlist('x_firstdegree_attachment')
              import base64
              if attached_files:
                 firstdegreefiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  firstdegreefiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_firstdegree_attachment',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_postdegree_attachment' in request.params:
              attached_files = request.httprequest.files.getlist('x_postdegree_attachment')
              import base64
              if attached_files:
                 postdegreefiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  postdegreefiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_postdegree_attachment',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })


        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = pedata.x_photo
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = pedata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = pedata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = pedata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = pedata.x_nrc_photo_back_name
        if post.get('x_firstdegree_attachment'):
           FileStorage = post.get('x_firstdegree_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_firstdegree_attachment = base64.encodestring(FileData)
        if not post.get('x_firstdegree_attachment'):
           x_firstdegree_attachment = pedata.x_firstdegree_attachment
        if post.get('x_firstdegree_filename'):
           x_firstdegree_filename = post.get('x_firstegree_filename')
        if not post.get('x_firstdegree_filename'):
           x_firstdegree_filename = pedata.x_firstdegree_filename
        if post.get('x_postdegree_attachment'):
           FileStorage = post.get('x_postdegree_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_postdegree_attachment = base64.encodestring(FileData)
        if not post.get('x_postdegree_attachment'):
           x_postdegree_attachment = pedata.x_postdegree_attachment
        if post.get('x_postdegree_filename'):
           x_postdegree_filename = post.get('x_postegree_filename')
        if not post.get('x_postdegree_filename'):
           x_postdegree_filename = pedata.x_postdegree_filename
        if post.get('x_others_qualification_attachment'):
           FileStorage = post.get('x_others_qualification_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_others_qualification_attachment = base64.encodestring(FileData)
        if not post.get('x_others_qualification_attachment'):
           x_others_qualification_attachment = pedata.x_others_qualification_attachment
        if post.get('x_others_filename'):
           x_others_filename = post.get('x_others_filename')
        if not post.get('x_others_filename'):
           x_others_filename = pedata.x_others_filename
        if post.get('x_career_attachments'):
           FileStorage = post.get('x_career_attachments')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_career_attachments = base64.encodestring(FileData)
        if not post.get('x_career_attachments'):
           x_career_attachments = pedata.x_career_attachments
        if post.get('x_career_filename'):
           x_career_filename = post.get('x_career_filename')
        if not post.get('x_career_filename'):
           x_career_filename = pedata.x_career_filename
        if post.get('x_career_attachment1'):
           FileStorage = post.get('x_career_attachment1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_career_attachment1 = base64.encodestring(FileData)
        if not post.get('x_career_attachment1'):
           x_career_attachment1 = pedata.x_career_attachment1
        if post.get('x_career_filename1'):
           x_career_filename1 = post.get('x_career_filename1')
        if not post.get('x_career_filename1'):
           x_career_filename1 = pedata.x_career_filename1
        if post.get('x_career_attachment2'):
           FileStorage = post.get('x_career_attachment2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_career_attachment2 = base64.encodestring(FileData)
        if not post.get('x_career_attachment2'):
           x_career_attachment2 = pedata.x_career_attachment2
        if post.get('x_career_filename2'):
           x_career_filename2 = post.get('x_career_filename2')
        if not post.get('x_career_filename2'):
           x_career_filename2 = pedata.x_career_filename2
        if post.get('x_program_certificates'):
           FileStorage = post.get('x_program_certificates')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_program_certificates = base64.encodestring(FileData)
        if not post.get('x_program_certificates'):
           x_program_certificates = pedata.x_program_certificates
        if post.get('x_program_filename'):
           x_program_filename = post.get('x_program_filename')
        if not post.get('x_program_filename'):
           x_program_filename = pedata.x_program_filename
        if post.get('x_program_certificate1'):
           FileStorage = post.get('x_program_certificate1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_program_certificate1 = base64.encodestring(FileData)
        if not post.get('x_program_certificate1'):
           x_program_certificate1 = pedata.x_program_certificate1
        if post.get('x_program_filename1'):
           x_program_filename1 = post.get('x_program_filename1')
        if not post.get('x_program_filename1'):
           x_program_filename1 = pedata.x_program_filename1
        if post.get('x_program_certificate2'):
           FileStorage = post.get('x_program_certificate2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_program_certificate2 = base64.encodestring(FileData)
        if not post.get('x_program_certificate2'):
           x_program_certificate2 = pedata.x_program_certificate2
        if post.get('x_program_filename2'):
           x_program_filename2 = post.get('x_program_filename2')
        if not post.get('x_program_filename2'):
           x_program_filename2 = pedata.x_program_filename2
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = pedata.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = pedata.x_other_attachment_name_1


        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = pedata.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = pedata.x_other_attachment_name_2


        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = pedata.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = pedata.x_other_attachment_name_3

        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = pedata.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = pedata.x_other_attachment_name_4

        if not post.get('x_st_state1'):
           state1 = pedata.x_st_state1
        if post.get('x_st_state1'):
           state1 = post.get('x_st_state1')
        if not post.get('x_st_state2'):
           state2 = pedata.x_st_state2
        if post.get('x_st_state2'):
           state2 = post.get('x_st_state2')
        if not post.get('x_tp_township1'):
           township1 = pedata.x_tp_township1
        if post.get('x_tp_township1'):
           township1 = post.get('x_tp_township1')
        if not post.get('x_tp_township2'):
           township2 = pedata.x_tp_township2
        if post.get('x_tp_township2'):
           township2 = post.get('x_tp_township2')
  
        # if post.get('x_payment_attachment'):
          # FileStorage = post.get('x_payment_attachment')
          # FileExtension = FileStorage.filename.split('.')[-1].lower()
          # ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
          # if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
          #     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
          # import base64
          # FileData = FileStorage.read()
          # x_payment_attachment = base64.encodestring(FileData)
       # if post.get('x_others_qualification_attachment'):
          # FileStorage = post.get('x_others_qualification_attachment')
          # FileExtension = FileStorage.filename.split('.')[-1].lower()
          # ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
          # if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
          #     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
          # import base64
          # FileData = FileStorage.read()
          # x_others_qualification_attachment = base64.encodestring(FileData)
       # if post.get('x_nrc_photo_front'):
       #    nrc = post.get('x_nrc_photo_front')
       # if post.get('x_nrc_photo_front_name'):
       #    nrcname = post.get('x_nrc_photo_front_name')
        Job = request.env['hr.applicant'].sudo().search([('id','=',peid)])
        if Job:
            val = {
                    'x_reg_no':post.get('x_reg_no'),
                    'x_gender':post.get('x_gender'),
                    'x_dob':post.get('x_dob'),
                    'x_name_mm':post.get('x_name_mm'),
                    'x_father_en':post.get('x_father_en'),
                    'x_father_mm':post.get('x_father_mm'),
                    'x_nrc_no_en':post.get('x_nrc_no_en'),
                    'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                    'partner_name':post.get('partner_name'),
                    'email_from':post.get('email_from'),
                    'x_per_email':post.get('x_per_email'),
                    'partner_phone':post.get('partner_phone'),
                    'x_per_tel_no':post.get('x_per_tel_no'),
                    'x_nrc_photo_front':x_nrc_photo_front,
                   # 'x_nrc_photo_front':post.get('x_nrc_photo_front'),
                    'x_nrc_photo_front_name':x_nrc_photo_front_name,
                    'x_nrc_photo_back':x_nrc_photo_back,
                    'x_nrc_photo_back_name':x_nrc_photo_back_name,
                    'x_photo':x_photo,
                    'x_title':post.get('x_title'),
                    'x_address_en':post.get('x_address_en'),
                    'x_per_address_en':post.get('x_per_address_en'),
                    'x_city_state':post.get('x_city_state'),
                    'x_per_state':post.get('x_per_state'),
                    'x_township':post.get('x_township'),
                    'x_per_township':post.get('x_per_township'),
                    'x_postcode':post.get('x_postcode'),
                    'x_per_postcode':post.get('x_per_postcode'),
                    'x_per_tel_no':post.get('x_per_tel_no'),
                    'x_fax_no':post.get('x_fax_no'),
                    'x_per_fax_no':post.get('x_per_fax_no'),
                    #'x_per_email':post.get('x_per_eamil'),
                    'x_address_mm':post.get('x_address_mm'),
                    'x_per_address_mm':post.get('x_per_address_mm'),
                    'x_firstdegree_uni':post.get('x_firstdegree_uni'),
                    'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                    'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                    'x_firstdegree_attachment':x_firstdegree_attachment,
                    'x_postdegree_uni':post.get('x_postdegree_uni'),
                    'x_postdegree_graduation_year':post.get('x_postdegree_graduation_year'),
                    'x_postdegree_engineer_discipline':post.get('x_postdegree_engineer_discipline'),
                    'x_postdegree_attachment':x_postdegree_attachment,
                    'x_others_qualification':post.get('x_others_qualification'),
                    'x_others_graduation_year':post.get('x_others_graduation_year'),
                   # 'x_discipline':post.get('x_discipline'),
                    'x_others_engineer_discipline':post.get('x_others_engineer_discipline'),
                    'x_others_qualification_attachment':x_others_qualification_attachment,
                   # 'x_career_attachments':x_career_attachments,
                   # 'x_career_attachment1':x_career_attachment1,
                   # 'x_career_attachment2':x_career_attachment2,
                   # 'x_program_certificates':x_program_certificates,
                   # 'x_program_certificate1':x_program_certificate1,
                   # 'x_program_certificate2':x_program_certificate2,
                    'x_work_fifteen_year':post.get('x_work_fifteen_year'),
                    'x_meet_requirement':post.get('x_meet_requirement'),
                    'x_no_discipline':post.get('x_no_discipline'),
                    'x_firstdegree_filename':x_firstdegree_filename,
                    'x_postdegree_filename':x_postdegree_filename,
                    'x_others_filename':x_others_filename,
                    'x_career_filename':x_career_filename,
                    'x_career_filename1':x_career_filename1,
                    'x_career_filename2':x_career_filename2,
                    'x_program_filename':x_career_filename,
                    'x_program_filename1':x_career_filename1,
                    'x_program_filename2':x_program_filename2,
                   # 'x_discipline': post.get('x_discipline'),
                   # 'x_payment_attachment':x_payment_attachment,
                   # 'x_other_attachments':x_other_attachments,
                    'partner_id':post.get('partner_id'),
                    'x_nrc1en':post.get('x_nrc1en'),
                    'x_nrc2en':post.get('x_nrc2en'),
                    'x_nrc3en':post.get('x_nrc3en'),
                    'x_nrc4en':post.get('x_nrc4en'),
                    'x_nrc1mm':post.get('x_nrc1mm'),
                    'x_nrc2mm':post.get('x_nrc2mm'),
                    'x_nrc3mm':post.get('x_nrc3mm'),
                    'x_nrc4mm':post.get('x_nrc4mm'),
                    'x_discipline_s':post.get('x_discipline_s'),
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                    'x_st_state1': state1,
                    'x_st_state2': state2,
                    'x_tp_township1':township1,
                    'x_tp_township2':township2,
                }
            Job.sudo().write(val)
            if post.get('x_discipline'):
               Job.sudo().write(vals)
               Job.sudo().write(value)
        #Job.sudo().write(post)
        name = 1
       # testfiles = request.env['ir.attachment'].sudo().search([('res_id','=',264)])
        pedatas = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',pedata.id)])
        pecount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',pedata.id)])
        return http.request.render('website.peproexperienceforms',{'pedata':pedatas,'sresult':name,'peid':peid,'pecount':pecount})

    @http.route(['/peregistrationform'], type='http', auth='public', website=True)
    def pe_data(self, **kw):
          pid = kw.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          st = http.request.env['x_state'].sudo().search([])
          township = http.request.env['x_township'].sudo().search([])
          todaydate =  fields.Datetime.now()
          pdata1 = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)])
          if pdata1:
             lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
          if not pdata1:
             lid = ' '
          return http.request.render('website.peregistrationform', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'lid':lid,'todaydate':todaydate,'st':st,'township':township})

    @http.route(['/previouspeproexperience3'], type='http', auth='public', website=True)
    def back_verify(self, **kw):
         #name = kw.get('name')
         #if not name:
             #name = 1
        # peid = kw.get('id')
         #peid = post.get('1-x_applicant')
         pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
         peid = pe.id
         #return request.redirect('/previouspeproexperience3?msg1=2')
         #peid = request.website._website_form_last_record().sudo().id
         pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',peid)])
         pcount = http.request.env['x_verify'].sudo().search_count([('x_applicant','=',peid)])
         return http.request.render('website.peverify', {'pedata': pedata, 'pcount': pcount,'peid': peid})

#    @http.route('/my-registration-list', auth='public',method='POST', website=True)
#    def registrationlist(self, **kw):
#        type=kw.get('name')
#        val = request.env.user.partner_id.id
#        reglists = http.request.env['hr.applicant'].sudo().search(['&',('partner_id.id','=',val),('job_id','=',1)])
#        lists = http.request.env['hr.applicant'].sudo().search([])
#        return http.request.render('website.my-registration-list', {'reglists': reglists, 'lists': lists})


    @http.route('/my-rsec-registration-list', auth='public', website=True)
    def reec_registrationlist(self, **kw):
        val = request.env.user.partner_id.id
       # peid = request.website._website_form_last_record().sudo().id
        reglists = http.request.env['hr.applicant'].sudo().search(['&',('partner_id.id','=',val),('job_id','=',5)])
       # lists = http.request.env['hr.applicant'].sudo().search(['&',('partner_id.id','=',val),('job_id','=',5)])
        lists = http.request.env['hr.applicant'].sudo().search([('job_id','=',5)])
        return http.request.render('website.my-rsec-registration-list', {'reglists': reglists, 'lists': lists})

    @http.route(['/pe_exp1'], type='http', auth='public', website=True)
    def pe_exp1(self, **kw):
          peid = kw.get('id')
          pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          pedata = http.request.env['x_involve'].sudo().search([('x_applicant','=',pdata1.id)])
          pecount = http.request.env['x_involve'].sudo().search_count([('x_applicant','=',pdata1.id)])
          if not peid:
             pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
             peid = pe.id
          return http.request.render('website.step-3', {'pedata': pedata, 'peid': peid, 'pdata1': pdata1,'sresult':1,'pecount': pecount})

    @http.route(['/pe_exp'], type='http', auth='public', website=True)
    def pe_exp(self, **kw):
          peid = kw.get('id')
          name = 1
          pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',pdata1.id)])
          pecount = http.request.env['x_proexperience'].sudo().search_count([('x_applicant','=',pdata1.id)])
          if not peid:
             pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
             peid = pe.id
          return http.request.render('website.step-2', {'pedata': pedata, 'peid': peid, 'pdata1': pdata1,'sresult':name,'pecount':pecount})

    @http.route(['/pe_exp2'], type='http', auth='public', website=True)
    def pe_exp2(self, **kw):
          peid = kw.get('id')
          pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          pedata = http.request.env['x_summary'].sudo().search([('x_applicant','=',pdata1.id)])
          pecount = http.request.env['x_summary'].sudo().search_count([('x_applicant','=',pdata1.id)])
          if not peid:
             pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
             peid = pe.id
          return http.request.render('website.step-4', {'pedata': pedata, 'peid': peid, 'pdata1': pdata1,'sresult':1,'pecount':pecount})

    @http.route(['/pe_exp3'], type='http', auth='public', website=True)
    def pe_exp3(self, **kw):
          peid = kw.get('id')
          pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          pedata = http.request.env['x_verify'].sudo().search([('x_applicant','=',pdata1.id)])
          pecount = http.request.env['x_verify'].sudo().search_count([('x_applicant','=',pdata1.id)])
          if not peid:
             pe = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
             peid = pe.id
          return http.request.render('website.step-5', {'pedata': pedata, 'pdata1': pdata1,'peid':peid,'sresult':1,'pecount':pecount})

    @http.route(['/approve-form'], type='http', auth='public', website=True)
    def apv_form(self, **kw):
          peid = kw.get('id')
          pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
          return http.request.render('website.approve-form', {'pdata1': pdata1})

    @http.route(['/peregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_data(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1 
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 1,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        st = http.request.env['x_state'].sudo().search([])
        township = http.request.env['x_township'].sudo().search([])
        state = http.request.env['x_state'].sudo().search([])
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',1)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.peregistrationform',{'pre_id':pre_id,'state':state,'st':st, 'township':township, 'nrc':nrc, 'nrcmm':nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata}) 


    @http.route(['/rsecregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rsec(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 5,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',5)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',5)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rsec-registration-form',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})

    @http.route(['/rtcregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rtc(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 3,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',3)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',3)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rtcregistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})
        

    @http.route(['/acperegistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_acpe(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 2,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',2)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.acperegistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})
        
    @http.route(['/rgtcregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rgtc(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 4,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',4)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',4)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rgtcregistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})

    @http.route(['/rfperegistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rfpe(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 8,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',8)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',8)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rfperegistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})
        #val = {
              #'x_user' : request.env.user.partner_id.id,
              #'x_job_id' : 8,
              #'x_f1' : post.get('x_f1'),
              #'x_f2' : post.get('x_f2'),
              #'x_f3' : post.get('x_f3'),
              #'x_f4' : post.get('x_f4'),
              #'x_f5' : post.get('x_f5')
            #}
        #user_preid = request.env['x_user_prerequest'].sudo().create(val)
        #if user_preid:
            #return request.redirect('/rfperegistrationform')

    #@http.route(['/rleregistrationform1'], type='http', auth='public', website=True, method='POST')
    #def preq_rle(self, **post):
    #    val = {
    #          'x_user' : request.env.user.partner_id.id,
    #          'x_job_id' : 6,
    #          'x_f1' : post.get('x_f1'),
    #          'x_f2' : post.get('x_f2'),
    #          'x_f3' : post.get('x_f3'),
    #          'x_f4' : post.get('x_f4'),
    #          'x_f5' : post.get('x_f5')
    #        }
    #    user_preid = request.env['x_user_prerequest'].sudo().create(val)
    #    if user_preid:
    #        return request.redirect('/rleregistrationform')

    @http.route(['/rleregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rle(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 6,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',6)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',6)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rleregistrationform',{'pre_id':pre_id,'lid': lid, 'todaydate':todaydate, 'ddata':ddata})

    @http.route(['/rlperegistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rlpe(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 7,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',7)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',7)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.rlperegistrationform',{'pre_id':pre_id,'lid': lid, 'todaydate':todaydate, 'ddata':ddata})
        #return request.redirect('//rlperegistrationform')

    @http.route(['/recregistration_back'], type='http', auth='public', webstie=True)
    def recregistration_back(self, **kw):
        #pre_id = kw.get('pre_id')
        #type = kw.get('pre_type')
        #pre_type = int(type)
        #userpre_data = http.request.env['x_user_prerequistic'].sudo().search([('id','=',287)])
        predata = http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',10)])
        return http.request.render('website.pre-request', {'predata':predata,'type': '10'})
        #predata = http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',jobid)])
        #return http.request.render('website.pre-request',{'type':type,'predata':predata})



    @http.route(['/recregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rec(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 10,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',10)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',10)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.recregistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate, 'ddata':ddata})
        #return request.redirect('/recregistrationform')

    @http.route(['/aecregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_aec(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 9,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',9)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',9)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.aecregistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})
        
    @http.route(['/atechregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_atech(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 11,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',11)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',11)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.atechregistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})

    @http.route(['/agtechregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_agtech(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 12,
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.agtechregistrationform',{'pre_id':pre_id, 'nrc': nrc, 'nrcmm': nrcmm, 'lid': lid, 'todaydate':todaydate,'ddata':ddata})

    @http.route(['/rsecrenewalregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rsecrenewal(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 16,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        userid = request.env.user.partner_id.id
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',5),('partner_id','=',userid)],order="id desc", limit=1)
        return http.request.render('website.rsec-renewal-registration',{'pre_id':pre_id, 'nrc':nrc, 'nrcmm':nrcmm,'sample':sample,'old_data':old_data})


    @http.route(['/recrenewalregistrationform'], type='http', auth='public', website=True, method='POST')
    def preq_recrenewal(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 14,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        userid = request.env.user.partner_id.id
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',10),('partner_id','=',userid)],order="id desc", limit=1)
        return http.request.render('website.rec-renewal-registration',{'pre_id':pre_id, 'nrc':nrc, 'nrcmm':nrcmm,'sample':sample,'old_data':old_data})

    @http.route(['/rlerenewalregistrationform'], type='http', auth='public', website=True, method='POST')
    def preq_rlerenewal(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 30,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        userid = request.env.user.partner_id.id
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',6),('partner_id','=',userid)],order="id desc", limit=1)
        return http.request.render('website.rle-renewal-registration',{'pre_id':pre_id, 'nrc':nrc, 'nrcmm':nrcmm,'sample':sample,'old_data':old_data})

    @http.route(['/rlperenewalregistrationform'], type='http', auth='public', website=True, method='POST')
    def preq_rlperenewal(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 31,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        userid = request.env.user.partner_id.id
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',7),('partner_id','=',userid)],order="id desc", limit=1)
        return http.request.render('website.rlpe-renewal-registration',{'pre_id':pre_id, 'nrc':nrc, 'nrcmm':nrcmm,'sample':sample,'old_data':old_data})


    @http.route(['/rfperenewalregistrationform'], type='http', auth='public', website=True, method='POST')
    def preq_rfperenewal(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 29,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        userid = request.env.user.partner_id.id
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',8),('partner_id','=',userid)],order="id desc", limit=1)
        return http.request.render('website.rfpe-renewal-registration',{'pre_id':pre_id, 'nrc':nrc, 'nrcmm':nrcmm,'sample':sample,'old_data':old_data})


    @http.route(['/perenewalregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_perenewal(self, **post):
        list_id = request.httprequest.form.getlist('x_prerequistic_id')
        sample = http.request.env['ir.attachment'].sudo().search([('x_field','=','sample_download')])
        count = 0
        vals = []
        for mm in list_id:
            vals.append(list_id[count])
            count = count + 1
        val = {
              'x_user_id' : request.env.user.partner_id.id,
              'x_job_id' : 13,
              #'x_prerequistic_id' :  [(6, 0,[mm for mm in list_id])]
              'x_prerequistic_id': [(6, 0, vals)]
            }
        preid=post.get('pre_id')
        if preid:
           userpre_id=int(preid)
           userdata = http.request.env['x_user_prerequistic'].sudo().search([('id','=',userpre_id)])
           res=userdata.sudo().unlink()
        updata=http.request.env['x_user_prerequistic'].sudo().create(val)
        pre_id=updata.id
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        userid = request.env.user.partner_id.id
        old_data = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',1),('partner_id','=',userid)],order="id desc", limit=1)
        return http.request.render('website.perenewalregistrationform',{'pre_id':pre_id, 'nrc':nrc, 'nrcmm':nrcmm,'sample':sample,'old_data':old_data})

    @http.route(['/rerenewalregistrationform1'], type='http', auth='public', website=True, method='POST')
    def preq_rerenewal(self, **post):
        val = {
              'x_user' : request.env.user.partner_id.id,
              'x_job_id' : 13,
              'x_f1' : post.get('x_f1'),
              'x_f2' : post.get('x_f2'),
              'x_f3' : post.get('x_f3'),
              'x_f4' : post.get('x_f4'),
              'x_f5' : post.get('x_f5')
            }
        user_preid = request.env['x_user_prerequest'].sudo().create(val)
        if user_preid:
            return request.redirect('/rerenewalregistrationform')

    @http.route(['/rserenewalform1'], type='http', auth='public', website=True, method='POST')
    def preq_rserenewal(self, **post):
        val = {
              'x_user' : request.env.user.partner_id.id,
              'x_job_id' : 5,
              'x_f1' : post.get('x_f1'),
              'x_f2' : post.get('x_f2'),
              'x_f3' : post.get('x_f3'),
              'x_f4' : post.get('x_f4'),
              'x_f5' : post.get('x_f5')
            }
        user_preid = request.env['x_user_prerequest'].sudo().create(val)
        if user_preid:
            return request.redirect('/rse-renewal')

    @http.route(['/pre-request'], type='http', auth='public', website=True, method='POST')
    def prequest(self, **kw):
        type = kw.get('id')
        userid = request.env.user.partner_id.id
        jobid = int(type)
        if jobid == 13:
           has_form = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',1),('partner_id','=',userid)],order="id desc", limit=1)
           if has_form:
              renew = http.request.env['x_renewal'].sudo().search(['&','&',('x_user_id','=',userid),('x_application_type','=',1),('x_applicant_id','=',has_form.id)])
        if jobid == 14:
           has_form = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',10),('partner_id','=',userid)],order="id desc", limit=1)
           if has_form:
              renew = http.request.env['x_renewal'].sudo().search(['&','&',('x_user_id','=',userid),('x_application_type','=',10),('x_applicant_id','=',has_form.id)])
        if jobid == 16:
           has_form = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',5),('partner_id','=',userid)],order="id desc", limit=1)
           if has_form:
              renew = http.request.env['x_renewal'].sudo().search(['&','&',('x_user_id','=',userid),('x_application_type','=',5),('x_applicant_id','=',has_form.id)])
        if jobid == 29:
           has_form = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',8),('partner_id','=',userid)],order="id desc", limit=1)
           if has_form:
              renew = http.request.env['x_renewal'].sudo().search(['&','&',('x_user_id','=',userid),('x_application_type','=',8),('x_applicant_id','=',has_form.id)])
        if jobid == 13 or jobid == 14 or jobid == 16 or jobid == 29:
           if has_form and renew:
              return request.redirect('/my-record')
           if has_form and not renew:
              pereq = http.request.env['ir.attachment'].sudo().search([('x_field','=','pereq')])
              rsereq = http.request.env['ir.attachment'].sudo().search([('x_field','=','rsereq')])
              predata = http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',jobid)])
              return http.request.render('website.pre-request',{'type':type,'predata':predata,'pereq':pereq,'rsereq':rsereq})
        if jobid != 13 and jobid != 14 and jobid != 16 and jobid != 29:
           has_form = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jobid),('partner_id','=',userid)],order="id desc", limit=1)
           if has_form:
              if has_form.x_state != '3':
                 return request.redirect('/my-record')
              if has_form.x_state == '3':
                 pereq = http.request.env['ir.attachment'].sudo().search([('x_field','=','pereq')])
                 rsereq = http.request.env['ir.attachment'].sudo().search([('x_field','=','rsereq')])
                 predata = http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',jobid)])
                 return http.request.render('website.pre-request',{'type':type,'predata':predata,'pereq':pereq,'rsereq':rsereq})
           if not has_form:
              pereq = http.request.env['ir.attachment'].sudo().search([('x_field','=','pereq')])
              rsereq = http.request.env['ir.attachment'].sudo().search([('x_field','=','rsereq')])
              predata = http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',jobid)])
              return http.request.render('website.pre-request',{'type':type,'predata':predata,'pereq':pereq,'rsereq':rsereq})

    @http.route(['/registration_back'], type='http', auth='public', website=True)
    def recregristration_back(self,**kw):
       # jobid=kw.get('id')
        pre_id=kw.get('pre_id')
        pretype=kw.get('pre_type')
        if pretype:
           jobid=int(pretype)
       # jobid=int(type) 
        userpre_data=http.request.env['x_user_prerequistic'].sudo().search([('id','=',pre_id)])
        predata=http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',jobid)])
        return http.request.render('website.pre-request',{'type':pretype,'predata':predata,'userpre_data':userpre_data,'pretype':pretype,'pre_id':pre_id})

    @http.route(['/recregistrationform'], type='http', auth='public', website=True)
    def rec_data(self, **kw):
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',10)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',10)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' '
        return http.request.render('website.recregistrationform', {'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'todaydate':todaydate,'lid':lid})

    @http.route(['/recregistrationformupdate'], type='http', auth='public', website=True)
    def rec_update(self, **kw):
        pid = kw.get('id')
        peid = request.website._website_form_last_record().sudo().id
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        return http.request.render('website.recregistrationform', {'pdata':pdata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'anotherfiles':anotherfiles})

    @http.route('/previousrec', type='http', auth='public', website=True, method='POST')
    def previous_rec(self, **kw):
        pid = kw.get('id')
       # peid = request.website._website_form_last_record().sudo().id
        predata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        type = 'REC'
        return http.request.render('website.reviewregistrationform', {'type':type,'predata':predata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'anotherfiles':anotherfiles})

    @http.route(['/recregistrationformupdate1'], type='http', auth='public', website=True,metho=['POST'])
    def rec_submit(self, **post):
        peid = post.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        dis = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        date =  fields.Datetime.now()
        adate = date.date()
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'4', 'x_applicant_id': peid, 'x_job_id': 10}
        history.sudo().create(hvalue)
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value = {
                           'x_discipline':[(6, 0, val)]
                    }
                    vals = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        #'name': attachment.filename,
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_another' in request.params:
              attached_files = request.httprequest.files.getlist('x_another')
              import base64
              if attached_files:
                 anotherfiles.sudo().unlink()
              for attachment in attached_files:
                  attached_file = attachment.read()
                  anotherfiles.sudo().create({
                        'name': attachment.filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_another',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })

        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = pdata.x_photo
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = pdata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = pdata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = pdata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = pdata.x_nrc_photo_back_name
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = pdata.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = pdata.x_other_attachment_name_1


        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = pdata.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = pdata.x_other_attachment_name_2


        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = pdata.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = pdata.x_other_attachment_name_3

        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = pdata.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = pdata.x_other_attachment_name_4
        Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        if Job:
            val = {
                    'x_state':4,
                    'x_reg_no':post.get('x_reg_no'),
                   # 'x_title':post.get('x_title'),
                    'x_dob':post.get('x_dob'),
                    'x_name_mm':post.get('x_name_mm'),
                    'x_father_en':post.get('x_father_en'),
                    'x_father_mm':post.get('x_father_mm'),
                    'x_nrc_no_en':post.get('x_nrc_no_en'),
                    'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                    'partner_name':post.get('partner_name'),
                    'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                    'x_address_en':post.get('x_address_en'),
                    'x_address_mm':post.get('x_address_mm'),
                    'partner_phone':post.get('partner_phone'),
                    'x_nrc_photo_front':x_nrc_photo_front,
                    'x_nrc_photo_front_name':x_nrc_photo_front_name,
                    'x_nrc_photo_back':x_nrc_photo_back,
                    'x_nrc_photo_back_name':x_nrc_photo_back_name,
                    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_nrc1en':post.get('x_nrc1en'),
                    'x_nrc2en':post.get('x_nrc2en'),
		    'x_nrc3en':post.get('x_nrc3en'),
		    'x_nrc4en':post.get('x_nrc4en'),
		    'x_nrc1mm':post.get('x_nrc1mm'),
		    'x_nrc2mm':post.get('x_nrc2mm'),
		    'x_nrc3mm':post.get('x_nrc3mm'),
		    'x_nrc4mm':post.get('x_nrc4mm'),
                    'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                    'x_form_status':4,
                    'x_discipline_s':post.get('x_discipline_s'),
                    'x_applied_date': adate,
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                 }
        Job.sudo().write(val)
        Job.sudo().write(vals)
        Job.sudo().write(value)
        type = 'REC'
        hid = str(peid)
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for apprentice engineer certificate with reg no REC-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
          # return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':id,'pdata1':pdata1})
        if not y["state"]:
           return request.redirect('/home')


    @http.route(['/atechregistrationform'], type='http', auth='public', website=True)
    def atech_data(self, **kw):
        #pid = kw.get('id')
        #peid = request.website._website_form_last_record().sudo().id
        #pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        todaydate =  fields.Datetime.now()
        pdata = http.request.env['hr.applicant'].sudo().search([('job_id','=',11)])
        if pdata:
           lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',11)], order="id desc", limit=1)[0]
        if not pdata:
           lid = ' ' 
        return http.request.render('website.atechregistrationform', {'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'todaydate':todaydate,'lid':lid})

    @http.route('/atechregistrationformupdate', type='http', auth='public', website=True, method=['POST'])
    def atech_update(self, **post):
       # pid = kw.get('id')
        peid = request.website._website_form_last_record().sudo().id
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
       # anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
        return http.request.render('website.atechregistrationform', {'pdata':pdata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles})

    @http.route('/previousatech', type='http', auth='public', website=True, method='POST')
    def previous_atech(self, **kw):
        pid = kw.get('id')
       # peid = request.website._website_form_last_record().sudo().id
        predata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
       # anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        type = 'ATech'
        return http.request.render('website.reviewregistrationform', {'type':type,'predata':predata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles})

    @http.route('/resubmitregistrationform', type='http', auth="public", methods=['POST'], website=True)
    def resubmit(self, **post):
        id = post.get('id')
        remark = post.get('x_test')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        val = {'x_state':2,'x_form_status':2}
        if pdata:
           pdata.sudo().write(val)
        job_id = pdata.job_id.id
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'2', 'x_applicant_id': id,'x_job_id': job_id }
        history.sudo().create(hvalue)
        adminemail = "mecportal20@gmail.com"
        useremail = pdata.email_from
        datemail = fields.Datetime.now().strftime('%B %d')
        subject = "Resubmit Mail"
        subjectmail = " "
        username = pdata.partner_name
        jobname = pdata.job_id.name
        regno = pdata.x_reg_no
        regbranch = "(01-2316995 / 01-2316891)"
        jname = pdata.job_id.x_job_name
        textaccept = "<p><span>Wrong entry of "+remark+" mentioned on your Academic Degree Certificate.</span></p>"
        message = "<table><tbody><tr><td><span>Dear "+username+"</span>"+textaccept+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
        y = send_email(useremail,message,subject)
        if y["state"]:
           url = jobname.lower()+'-registration-list'
           return http.request.redirect(url)
        if not y["state"]:
           return http.request.redirect('/home')
       # return http.request.render('website.form-records')

    @http.route('/rejectregistrationform', type='http', auth="public", method=['POST'], website=True)
    def reject(self, **post):
        id = post.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        val = {'x_state':3,'x_form_status':3}
        if pdata:
           pdata.sudo().write(val)
        job_id = pdata.job_id.id
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'3', 'x_applicant_id': id,'x_job_id': job_id }
        history.sudo().create(hvalue)
        adminemail = "mecportal20@gmail.com"
        useremail = pdata.email_from
        datemail = fields.Datetime.now().strftime('%B %d')
        subject = "Reject Mail"
        subjectmail = " "
        username = pdata.partner_name
        jobname = pdata.job_id.name
        regno = pdata.x_reg_no
        regbranch = "(01-2316995 / 01-2316891)"
        jname = pdata.job_id.x_job_name
        textaccept = "<p><span>Your Academic Qualification was not compliance to MEngC specification.</span></p>"
        message = "<table><tbody><tr><td><span>Dear "+username+"</span>"+textaccept+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
        y = send_email(useremail,message,subject)
        if y["state"]:
           url = jobname.lower()+'-registration-list'
           return http.request.redirect(url)
        if not y["state"]:
           return http.request.redirect('/home')
        #return http.request.render('website.form-records')

    @http.route('/atechregistrationformupdate1', type='http', auth="public", method=['POST'], website=True)
    def atechupdate1(self, **post):
        peid = post.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        date =  fields.Datetime.now()
        adate = date.date()
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
       # anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        dis = http.request.env['x_discipline'].sudo().search([])
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value = {
                           'x_discipline':[(6, 0, val)]
                    }
                    vals = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        #'name': attachment.filename,
                        'name':final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = pdata.x_photo
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = pdata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = pdata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = pdata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = pdata.x_nrc_photo_back_name
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = pdata.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = pdata.x_other_attachment_name_1
        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = pdata.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = pdata.x_other_attachment_name_2
        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = pdata.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = pdata.x_other_attachment_name_3
        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = pdata.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = pdata.x_other_attachment_name_4
        Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        if Job:
            val = {
                    'x_state':4,
                    'x_reg_no':post.get('x_reg_no'),
                   # 'x_title':post.get('x_title'),
                    'x_dob':post.get('x_dob'),
                    'x_name_mm':post.get('x_name_mm'),
                    'x_father_en':post.get('x_father_en'),
                    'x_father_mm':post.get('x_father_mm'),
                    'x_nrc_no_en':post.get('x_nrc_no_en'),
                    'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                    'partner_name':post.get('partner_name'),
                    'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                    'x_address_en':post.get('x_address_en'),
                    'x_address_mm':post.get('x_address_mm'),
                    'partner_phone':post.get('partner_phone'),
                    'x_nrc_photo_front':x_nrc_photo_front,
                    'x_nrc_photo_front_name':x_nrc_photo_front_name,
                    'x_nrc_photo_back':x_nrc_photo_back,
                    'x_nrc_photo_back_name':x_nrc_photo_back_name,
                    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_nrc1en':post.get('x_nrc1en'),
                    'x_nrc2en':post.get('x_nrc2en'),
                    'x_nrc3en':post.get('x_nrc3en'),
                    'x_nrc4en':post.get('x_nrc4en'),
                    'x_nrc1mm':post.get('x_nrc1mm'),
                    'x_nrc2mm':post.get('x_nrc2mm'),
                    'x_nrc3mm':post.get('x_nrc3mm'),
                    'x_nrc4mm':post.get('x_nrc4mm'),
                    'x_discipline_s':post.get('x_discipline_s'),
                    'x_form_status':4,
                    'x_applied_date': adate,
                    'x_academic_qualification':post.get('x_academic_qualification'),
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                  }
        Job.sudo().write(val)
        #Job.sudo().write(vals)
        #Job.sudo().write(value)
        type = 'ATech'
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        hid = ' '+peid+' '
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for apprentice technician with reg no ATech-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
           #return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':peid})
        if not y["state"]:
           return request.redirect('/home')

        #return http.request.render('website_hr_recruitment.thankyou', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'type':type})

    @http.route('/rgtechregistrationformupdate1', type='http', auth="public", method=['POST'], website=True)
    def rgtechupdate1(self, **post):
        peid = post.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        date =  fields.Datetime.now()
        adate = date.date()
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
       # anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',peid),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        dis = http.request.env['x_discipline'].sudo().search([])
        if dis:
            if post:
                res = 'no data'

                if post.get('x_discipline'):
                    list_id = request.httprequest.form.getlist('x_discipline')
                    count = 0
                    val = []
                    for mm in list_id:
                        val.append(list_id[count])
                        count = count + 1
                    value = {
                           'x_discipline':[(6, 0, val)]
                    }
                    vals = {
                           'x_discipline':[(5,)]
                   }
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        #'name': attachment.filename,
                        'name':final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': peid,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = pdata.x_photo
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = pdata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = pdata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = pdata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = pdata.x_nrc_photo_back_name
        if post.get('x_other_attachment_1'):
           FileStorage = post.get('x_other_attachment_1')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_1 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_1'):
           x_other_attachment_1 = pdata.x_other_attachment_1
        if post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = post.get('x_other_attachment_name_1')
        if not post.get('x_other_attachment_name_1'):
           x_other_attachment_name_1 = pdata.x_other_attachment_name_1
        if post.get('x_other_attachment_2'):
           FileStorage = post.get('x_other_attachment_2')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_2 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_2'):
           x_other_attachment_2 = pdata.x_other_attachment_2
        if post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = post.get('x_other_attachment_name_2')
        if not post.get('x_other_attachment_name_2'):
           x_other_attachment_name_2 = pdata.x_other_attachment_name_2
        if post.get('x_other_attachment_3'):
           FileStorage = post.get('x_other_attachment_3')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_3 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_3'):
           x_other_attachment_3 = pdata.x_other_attachment_3
        if post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = post.get('x_other_attachment_name_3')
        if not post.get('x_other_attachment_name_3'):
           x_other_attachment_name_3 = pdata.x_other_attachment_name_3
        if post.get('x_other_attachment_4'):
           FileStorage = post.get('x_other_attachment_4')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_other_attachment_4 = base64.encodestring(FileData)
        if not post.get('x_other_attachment_4'):
           x_other_attachment_4 = pdata.x_other_attachment_4
        if post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = post.get('x_other_attachment_name_4')
        if not post.get('x_other_attachment_name_4'):
           x_other_attachment_name_4 = pdata.x_other_attachment_name_4
        Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        if Job:
            val = {
                    'x_state':4,
                    'x_reg_no':post.get('x_reg_no'),
                   # 'x_title':post.get('x_title'),
                    'x_dob':post.get('x_dob'),
                    'x_name_mm':post.get('x_name_mm'),
                    'x_father_en':post.get('x_father_en'),
                    'x_father_mm':post.get('x_father_mm'),
                    'x_nrc_no_en':post.get('x_nrc_no_en'),
                    'x_nrc_no_mm':post.get('x_nrc_no_mm'),
                    'partner_name':post.get('partner_name'),
                    'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                    'x_address_en':post.get('x_address_en'),
                    'x_address_mm':post.get('x_address_mm'),
                    'partner_phone':post.get('partner_phone'),
                    'x_nrc_photo_front':x_nrc_photo_front,
                    'x_nrc_photo_front_name':x_nrc_photo_front_name,
                    'x_nrc_photo_back':x_nrc_photo_back,
                    'x_nrc_photo_back_name':x_nrc_photo_back_name,
                    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_nrc1en':post.get('x_nrc1en'),
                    'x_nrc2en':post.get('x_nrc2en'),
                    'x_nrc3en':post.get('x_nrc3en'),
                    'x_nrc4en':post.get('x_nrc4en'),
                    'x_nrc1mm':post.get('x_nrc1mm'),
                    'x_nrc2mm':post.get('x_nrc2mm'),
                    'x_nrc3mm':post.get('x_nrc3mm'),
                    'x_nrc4mm':post.get('x_nrc4mm'),
                    'x_discipline_s':post.get('x_discipline_s'),
                    'x_form_status':4,
                    'x_applied_date': adate,
                    'x_academic_qualification':post.get('x_academic_qualification'),
                    'x_other_attachment_1':x_other_attachment_1,
                    'x_other_attachment_name_1':x_other_attachment_name_1,
                    'x_other_attachment_2':x_other_attachment_2,
                    'x_other_attachment_name_2':x_other_attachment_name_2,
                    'x_other_attachment_3':x_other_attachment_3,
                    'x_other_attachment_name_3':x_other_attachment_name_3,
                    'x_other_attachment_4':x_other_attachment_4,
                    'x_other_attachment_name_4':x_other_attachment_name_4,
                    'x_other_attachments_filename_1':post.get('x_other_attachments_filename_1'),
                    'x_other_attachments_filename_2':post.get('x_other_attachments_filename_2'),
                    'x_other_attachments_filename_3':post.get('x_other_attachments_filename_3'),
                    'x_other_attachments_filename_4':post.get('x_other_attachments_filename_4'),
                  }
        Job.sudo().write(val)
        #Job.sudo().write(vals)
        #Job.sudo().write(value)
        type = 'RGTC'
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        hid = ' '+peid+' '
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',hid)])
        useremail = pdata1.email_from
        message = "Your registration for apprentice technician with reg no RGTC-"+hid+" has been summited"
        subject = "Submit Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           return http.request.redirect('/my-record')
           #return http.request.render('website_hr_recruitment.thankyou', {'type':type,'aid':peid})
        if not y["state"]:
           return request.redirect('/home')

        #return http.request.render('website_hr_recruitment.thankyou', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'type':type})

    @http.route(['/pe-renew-list','/pe-renew-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def pe_renew(self, page=1,**kw):
        start = '2021-02-01'
        end = fields.Datetime.now().date()
        testlist = http.request.env['hr.applicant'].sudo().search(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',1)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',1)])
        pager = request.website.pager( url='/pe-renew-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',1)])
        jname = job_lists.name
        return http.request.render('website.renew-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':1,'state': '22','cpdStatus': 1,'start':start, 'end':end})

    @http.route(['/rsec-renew-list','/rsec-renew-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def rsec_renew(self, page=1,**kw):
        start = '2021-02-01'
        end = fields.Datetime.now().date()
        testlist = http.request.env['hr.applicant'].sudo().search(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',5)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',5)])
        pager = request.website.pager( url='/rsec-renew-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',5)])
        jname = job_lists.name
        return http.request.render('website.rsec-renewal-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':5,'state':'22', 'start': start, 'end': end})

    @http.route(['/rec-renew-list','/rec-renew-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def rec_renew(self, page=1,**kw):
        start = '2021-02-01'
        end = fields.Datetime.now().date()
        testlist = http.request.env['hr.applicant'].sudo().search(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',10)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',10)])
        pager = request.website.pager( url='/rec-renew-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',10)])
        jname = job_lists.name
        return http.request.render('website.rec-renewal-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':10, 'state':'22','start': start, 'end': end})

    @http.route(['/rle-renew-list','/rle-renew-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def rle_renew(self, page=1,**kw):
        start = '2021-02-01'
        end = fields.Datetime.now().date()
        testlist = http.request.env['hr.applicant'].sudo().search(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',6)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',6)])
        pager = request.website.pager( url='/rle-renew-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',6)])
        jname = job_lists.name
        return http.request.render('website.rle-renew-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':6, 'state':'22','start': start, 'end': end})


    @http.route(['/rfpe-renew-list','/rfpe-renew-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def rfpe_renew(self, page=1,**kw):
        start = '2021-02-01'
        end = fields.Datetime.now().date()
        testlist = http.request.env['hr.applicant'].sudo().search(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',8)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',8)])
        pager = request.website.pager( url='/rfpe-renew-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',8)])
        jname = job_lists.name
        return http.request.render('website.rfpe-renew-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':8, 'state':'22','start': start, 'end': end})

    @http.route(['/rlpe-renew-list','/rlpe-renew-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def rlpe_renew(self, page=1,**kw):
        start = '2021-02-01'
        end = fields.Datetime.now().date()
        testlist = http.request.env['hr.applicant'].sudo().search(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',7)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','|','|','|',('x_state','=','22'),('x_state','=','23'),('x_state','=','24'),('x_state','=','25'),('job_id','=',7)])
        pager = request.website.pager( url='/rlpe-renew-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',7)])
        jname = job_lists.name
        return http.request.render('website.rlpe-renew-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':7, 'state':'22','start': start, 'end': end})

    @http.route(['/pe-registration-list','/pe-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def pe_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',1)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',1)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/pe-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.pe-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.pe-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route(['/acpe-registration-list','/acpe-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def acpe_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',2)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',2)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',2),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',2),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/acpe-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.acpe-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.acpe-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route(['/rtc-registration-list','/rtc-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def rtc_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',3)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',3)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',3),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',3),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rtc-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rtc-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rtc-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route(['/rgtc-registration-list','/rgtc-registration-list/page/<int:page>/'],  type='http', auth="public", website=True)
    def rgtc_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',4)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',4)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',4),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',4),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rgtc-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rgtc-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rgtc-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    #@http.route(['/rsec-registration-list','/rsec-registration-list/page/<int:page>/'],  type='http', auth="public", website=True)
    #def rsec_registration(self, page=1,**kw):
        #rsec_list = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',5)],offset=(page-1)*20, limit=20)
        #total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',5)])
        #pager = request.website.pager( url='/rsec-registration-list', total=total, page=page, step=20, scope=5 )
        #job_lists = http.request.env['hr.job'].sudo().search([('id','=',5)])
        #jname = job_lists.name
        #return http.request.render('website.rsec-registration-list',{'rsec_list':rsec_list,'pager':pager, 'jname':jname, 'jid':5})

    @http.route(['/rsec-registration-list','/rsec-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def rsec_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('rsecname')
        if name:
           name_lower = post.get('rsecname').lower()
           name_upper = post.get('rsecname').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',5)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',5)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                   url='/rsec-registration-list',
                   url_args= post,
                   total=total,
                   page=page,
                   step=20,
                   scope=5,
               )
        if res:
           return http.request.render('website.rsec-search-list', { 'rsec_list': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rsec-search-list', { 'rsec_list': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route(['/rle-registration-list','/rle-registration-list/page/<int:page>/'],method=['POST'], type='http', auth="public", website=True)
    def rle_registration(self, page=1,**post):
        testlist1 = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',6)],offset=(page-1)*20, limit=20)
        testlistaccept = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','7'),('job_id','=',6)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',6)])
        pager = request.website.pager( url='/rle-registration-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',6)])
        jname = job_lists.name
        jjid = post.get('jid');
        if jjid:
           jid = int(jjid)
        if not jjid:
           jid = ' '
        #jname = post.get('jname')
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        state = post.get('state')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        com_name = http.request.env['hr.applicant'].sudo().search([])
        if not state:
           val = request.env.user.partner_id.id
           acclists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)])
           testlist = http.request.env['hr.applicant'].sudo().search([])
           accdatas = []
           for acclist in testlist:
               accid = acclist.id
               accid1 = int(accid)
               aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
               accdatas.append(aapays)
           ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
           return http.request.render('website.rle-registration-list',{'testlist1':testlist1,'testlistaccept':testlistaccept,'pager':pager, 'jname':jname, 'jid':6,'accdatas':accdatas,'ilists':ilists})
        if com_name:
            jname = post.get('jname')
            #daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
            res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',jid),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
            total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
            #query = "select * from blog.post where name LIKE '%name%'"
            #request.cr.execute(query)
            #res = request.cr.fetchall()
            pager = request.website.pager(
                 url='/rle-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
            accdatas = []
            for acclist in res:
                accid = acclist.id
                accid1 = int(accid)
                aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                if aapays:
                   accdatas.append(aapays)
                   msg = 3
                if not aapays:
                   msg = 4
            idatas = []
            for ilist in res:
                aid = ilist.id
                apid = int(aid)
                idata = http.request.env['x_interview'].sudo().search(['&','&',('x_applicant_id','=',apid),('x_type','=',1),('x_status','=',1)])
                if idata:
                   idatas.append(idata)
                   msg = 3
                if not idata:
                   msg = 4
            if res:
                return http.request.render('website.rle-registration-list', {
                # pass company details to the webpage in a variable
                'testlist': res,'pager': pager,'now':now,'jname':jname,'name':name ,'jid':jid ,'state':state,'accdatas':accdatas,'msg':msg,'start':start,'end':end,'idatas':idatas})
            if not res:
                a = ()
                return http.request.render('website.rle-registration-list', {
                # pass company details to the webpage in a variable
                'testlist': a,'sresult':name, 'jid':jid,'start':start,'end':end,'state':state,'jname':jname,'name':name})

    @http.route(['/rlpe-registration-list','/rlpe-registration-list/page/<int:page>/'], type='http', auth="public",method=['POST'], website=True)
    def rlpe_registration(self, page=1,**post):
        testlist1 = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',7)],offset=(page-1)*20, limit=20)
        testlistaccept = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','7'),('job_id','=',7)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',7)])
        pager = request.website.pager( url='/rlpe-registration-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',7)])
        jname = job_lists.name
        #return http.request.render('website.rlpe-registration-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':7})
        jjid = post.get('jid');
        if jjid:
           jid = int(jjid)
        if not jjid:
           jid = ' '
        #jname = post.get('jname')
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        state = post.get('state')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        com_name = http.request.env['hr.applicant'].sudo().search([])
        if not state:
           val = request.env.user.partner_id.id
           acclists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)])
           testlist = http.request.env['hr.applicant'].sudo().search([])
           accdatas = []
           for acclist in testlist:
               accid = acclist.id
               accid1 = int(accid)
               aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
               accdatas.append(aapays)
           ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
           return http.request.render('website.rlpe-registration-list',{'testlist1':testlist1,'testlistaccept':testlistaccept,'pager':pager, 'jname':jname, 'jid':7})
        if com_name:
            jname = post.get('jname')
            #daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
            res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',jid),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
            total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
            #query = "select * from blog.post where name LIKE '%name%'"
            #request.cr.execute(query)
            #res = request.cr.fetchall()
            pager = request.website.pager(
                 url='/rlpe-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
            accdatas = []
            for acclist in res:
                accid = acclist.id
                accid1 = int(accid)
                aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                if aapays:
                   accdatas.append(aapays)
                   msg = 3
                if not aapays:
                   msg = 4
            idatas = []
            for ilist in res:
                aid = ilist.id
                apid = int(aid)
                idata = http.request.env['x_interview'].sudo().search(['&','&',('x_applicant_id','=',apid),('x_type','=',1),('x_status','=',1)])
                if idata:
                   idatas.append(idata)
                   msg = 3
                if not idata:
                   msg = 4
            if res:
                return http.request.render('website.rlpe-registration-list', {
                # pass company details to the webpage in a variable
                'testlist': res,'pager': pager,'now':now,'jname':jname,'name':name ,'jid':jid ,'state':state,'accdatas':accdatas,'msg':msg,'start':start,'end':end,'idatas':idatas})
            if not res:
                a = ()
                return http.request.render('website.rlpe-registration-list', {
                # pass company details to the webpage in a variable
                'testlist': a,'sresult':name, 'jid':jid,'start':start,'end':end,'state':state,'jname':jname,'name':name})


    @http.route(['/rfpe-registration-list','/rfpe-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'], website=True)
    def rfpe_registration(self, page=1,**post):
        testlist1 = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',8)],offset=(page-1)*20, limit=20)
        testlistaccept = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','7'),('job_id','=',8)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',8)])
        pager = request.website.pager( url='/rfpe-registration-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',8)])
        jname = job_lists.name
        #return http.request.render('website.rfpe-registration-list',{'testlist1':testlist1,'pager':pager, 'jname':jname, 'jid':8})
        jjid = post.get('jid');
        if jjid:
           jid = int(jjid)
        if not jjid:
           jid = ' '
        #jname = post.get('jname')
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        state = post.get('state')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        com_name = http.request.env['hr.applicant'].sudo().search([])
        if not state:
           val = request.env.user.partner_id.id
           acclists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)])
           testlist = http.request.env['hr.applicant'].sudo().search([])
           accdatas = []
           for acclist in testlist:
               accid = acclist.id
               accid1 = int(accid)
               aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
               accdatas.append(aapays)
           ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
           return http.request.render('website.rfpe-registration-list',{'testlist1':testlist1,'testlistaccept':testlistaccept,'pager':pager, 'jname':jname, 'jid':8,'accdatas':accdatas,'ilists':ilists})
        if com_name:
            jname = post.get('jname')
            #daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
            res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',jid),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
            total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
            #query = "select * from blog.post where name LIKE '%name%'"
            #request.cr.execute(query)
            #res = request.cr.fetchall()
            pager = request.website.pager(
                 url='/rfpe-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
            accdatas = []
            for acclist in res:
                accid = acclist.id
                accid1 = int(accid)
                aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                if aapays:
                   accdatas.append(aapays)
                   msg = 3
                if not aapays:
                   msg = 4
            idatas = []
            for ilist in res:
                aid = ilist.id
                apid = int(aid)
                idata = http.request.env['x_interview'].sudo().search(['&','&',('x_applicant_id','=',apid),('x_type','=',1),('x_status','=',1)])
                if idata:
                   idatas.append(idata)
                   msg = 3
                if not idata:
                   msg = 4
            if res:
                return http.request.render('website.rfpe-registration-list', {
                # pass company details to the webpage in a variable
                'testlist': res,'pager': pager,'now':now,'jname':jname,'name':name ,'jid':jid ,'state':state,'accdatas':accdatas,'msg':msg,'start':start,'end':end,'idatas':idatas})
            if not res:
                a = ()
                return http.request.render('website.rfpe-registration-list', {
                # pass company details to the webpage in a variable
                'testlist': a,'sresult':name, 'jid':jid,'start':start,'end':end,'state':state,'jname':jname,'name':name})


    @http.route(['/aec-registration-list','/aec-registration-list/page/<int:page>/'],  type='http', auth="public",method=['POST'], website=True)
    def aec_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',9)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',9)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',9),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',9),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/aec-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.aec-registration-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.aec-registration-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name})

    #@http.route(['/aec-registration-list','/aec-registration-list/page/<int:page>/'],  type='http', auth="public", website=True)
    #def aec_registration(self, page=1,**kw):
        #testlist = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',9)],offset=(page-1)*20, limit=20)
        #total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',9)])
        #pager = request.website.pager( url='/aec-registration-list', total=total, page=page, step=20, scope=5 )
        #job_lists = http.request.env['hr.job'].sudo().search([('id','=',9)])
        #jname = job_lists.name
        #return http.request.render('website.my-registration-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':9})

    @http.route(['/rec-registration-list','/rec-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def rec_registration(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',10)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',10)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',10),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',10),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rec-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rec-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rec-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route(['/atech-registration-list','/atech-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def atech_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',11)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',11)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',11),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',11),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/atech-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.atech-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.atech-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    #@http.route(['/agtech-registration-list','/agtech-registration-list/page/<int:page>/'],  type='http', auth="public", website=True)
    #def agtech_registration(self, page=1,**kw):
        #testlist = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',12)],offset=(page-1)*20, limit=20)
        #total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',12)])
        #pager = request.website.pager( url='/agtech-registration-list', total=total, page=page, step=20, scope=5 )
        #job_lists = http.request.env['hr.job'].sudo().search([('id','=',12)])
        #jname = job_lists.name
        #return http.request.render('website.my-registration-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':12})

    @http.route(['/agtech-registration-list','/agtech-registration-list/page/<int:page>/'],  type='http', auth="public", method=['POST'],website=True)
    def agtech_registration(self, page=1,**post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('agtechname')
        if name:
           name_lower = post.get('agtechname').lower()
           name_upper = post.get('agtechname').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '4'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','4'),('job_id','=',12)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','4'),('job_id','=',12)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',12),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',12),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/agtech-registration-list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.agtech-search-list', { 'agtech_list': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.agtech-search-list', { 'agtech_list': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route(['/my-registration-list','/my-registration-list/page/<int:page>/'],  type='http', auth="public", methods=['POST'],website=True)
    def myregistered_data(self, page=1,**post):
        jid=post.get('id')
        jobid = int(jid)
        testlist = http.request.env['hr.applicant'].sudo().search([('job_id','=',jobid)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count([('job_id','=',jobid)])
        pager = request.website.pager( url='/my-registration-list', total=total, page=page, step=20, scope=5 )
        job_lists = http.request.env['hr.job'].sudo().search([('id','=',jobid)])
        jname = job_lists.name
        return http.request.render('website.my-registration-list',{'testlist':testlist,'pager':pager, 'jname':jname, 'jid':jobid})

    @http.route('/mylistdetail', type='http', auth="public", method=['POST'], website=True)
    def my_listdetail(self, page=1, **post):
        jjid = post.get('jid');
        if jjid:
           jid = int(jjid)
        if not jjid:
           jid = ' '
        jname = post.get('jname')
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        state = post.get('state') 
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        com_name = http.request.env['hr.applicant'].sudo().search([])
        if com_name:
            #daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
            res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',jid),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
            total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
            #query = "select * from blog.post where name LIKE '%name%'"
            #request.cr.execute(query)
            #res = request.cr.fetchall()
            pager = request.website.pager(
                 url='/my-registration-list1',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
            accdatas = []
            for acclist in res:
                accid = acclist.id
                accid1 = int(accid)
                aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                if aapays:
                   accdatas.append(aapays)
                   msg = 3
                if not aapays:
                   msg = 4
            if res:
                return http.request.render('website.my-registration-list1', {
                # pass company details to the webpage in a variable
                'testlist': res,'pager': pager,'now':now,'jname':jname,'name':name ,'jid':jid ,'state':state,'accdatas':accdatas,'msg':msg,'start':start,'end':end})
            if not res:
                a = ()
                return http.request.render('website.my-registration-list1', {
                # pass company details to the webpage in a variable
                'testlist': a,'sresult':name, 'jid':jid,'start':start,'end':end,'state':state,'jname':jname,'name':name})

    @http.route('/new-formrecords-ui',  type='http', auth="public", website=True)
    def new_formrecords(self, **kw):
        type1=kw.get('name')
        if type1:
           type = int(type1)
        if not type1:
           type = ' '
        id1 = kw.get('id')
        if id1 :
           id = int(id1)
        if not id1:
           id = ' '
        states = http.request.env['hr.applicant'].sudo().search([('job_id','=',type)])
        press = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',type),('x_state','=',id)])
        save = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',1)])
        resubmit = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',2)])
        rejected = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',3)])
        submited = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',4)])
        accepted = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',5)])
        awaiting = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',7)])
        confirmed = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',8)])
        completed = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',9)])
        issued = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',type),('x_state','=',10)])
        return http.request.render('website.form-record-ui',{'type':type,'states':states,'save':save,'resubmit':resubmit,'rejected':rejected,'submited':submited,'accepted':accepted,'awaiting':awaiting,'confirmed':confirmed,'completed':completed,'issued':issued,'press':press,'id1':id1})

    @http.route('/agtech_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def agtech_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',12)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',12)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',12),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',12),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/agtech_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.agtech-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.agtech-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/atech_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def atech_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',11)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',11)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',11),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',11),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/atech_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.atech-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.atech-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/rgtc_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rgtc_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',4)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',4)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',4),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',4),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rgtc_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rgtc-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rgtc-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/rtc_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rtc_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',3)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',3)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',3),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',3),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rtc_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rtc-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rtc-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/aec_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def aec_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',9)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',9)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',9),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',9),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/aec_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.aec-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.aec-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route('/rec_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rec_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',10)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',10)])
        if post.get('state'):
           state = post.get('state')
           if state == '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',10),'&','|',('x_state','=','15'),('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',10),'&','|',('x_state','=',state),('x_state','=','15'),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
           if state != '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',10),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',10),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rec_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rec-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rec-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/acpe_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def acpe_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',2)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',2)])
        if post.get('state'):
           state = post.get('state')
           if state == '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',2),'&','|',('x_state','=','15'),('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',2),'&','|',('x_state','=',state),('x_state','=','15'),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
           if state != '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',2),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',2),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/acpe_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.acpe-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.acpe-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route('/rlpe_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rlpe_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',7)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',7)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',7),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',7),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rlpe_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rlpe-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rlpe-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route('/rfpe_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rfpe_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',8)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',8)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',8),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',8),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rfpe_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rfpe-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rfpe-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})



    @http.route('/rle_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rle_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',6)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',6)])
        if post.get('state'):
           state = post.get('state')
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',6),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',6),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rle_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rle-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rle-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})

    @http.route('/rsec_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def rsec_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',5)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',5)])
        if post.get('state'):
           state = post.get('state')
           if state == '16':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&','|',('x_state','=','19'),('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&','|',('x_state','=',state),('x_state','=','19'),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
           if state == '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&','|',('x_state','=','15'),('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&','|',('x_state','=',state),('x_state','=','15'),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
           if state != '16' and state != '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',5),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/rsec_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.rsec-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.rsec-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/pe_acceptance_list', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def pe_acceptance_list(self, page=1, **post):
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        if not post.get('state'):
           state = '7'
           res = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',state),('job_id','=',1)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',state),('job_id','=',1)])
        if post.get('state'):
           state = post.get('state')
           if state == '16':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&','|',('x_state','=','19'),('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&','|',('x_state','=',state),('x_state','=','19'),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
           if state == '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&','|',('x_state','=','15'),('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&','|',('x_state','=',state),('x_state','=','15'),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
           if state != '16' and state != '12':
              res = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_applied_date','>=',start),('x_applied_date','<=',end),'&',('job_id','=',1),'&',('x_state','=',state),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
        pager = request.website.pager(
                 url='/pe_acceptance_list',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
        if res:
           return http.request.render('website.pe-acceptance-list', { 'testlist': res,'pager': pager,'now':now,'name':name,'state':state,'start':start,'end':end})
        if not res:
           a = ()
           return http.request.render('website.pe-acceptance-list', { 'testlist': a,'start':start,'end':end,'state':state,'name':name,'pager':pager})


    @http.route('/acceptance-lists',  type='http', auth="public", website=True)
    def acceptance_lists(self, **kw):
        type= kw.get('name')
        val = request.env.user.partner_id.id
        acclists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)])
        testlist = http.request.env['hr.applicant'].sudo().search([])
        accdatas = []
        for acclist in testlist:
            accid = acclist.id
            accid1 = int(accid)
            aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
            accdatas.append(aapays)
        ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
        return http.request.render('website.acceptance-lists',{'testlist':testlist,'type':type,'accdatas':accdatas,'ilists':ilists})

    @http.route('/myacceptancedetail', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def myacceptance_searchdetail(self, page=1, **post):
        jjid = post.get('jid');
        if jjid:
           jid = int(jjid)
        if not jjid:
           jid = ' '
        jname = post.get('jname')
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        state = post.get('state')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        com_name = http.request.env['hr.applicant'].sudo().search([])
        if com_name:
            daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
            res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jid),'|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
            total = http.request.env['hr.applicant'].sudo().search_count(['|','|','|','|','|','|','|','|','|','|',('x_approval_no','ilike',name),('x_reg_no','ilike',name),('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
            #query = "select * from blog.post where name LIKE '%name%'"
            #request.cr.execute(query)
            #res = request.cr.fetchall()
            pager = request.website.pager(
                 url='/acceptance-lists-search',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
            accdatas = []
            for acclist in res:
                accid = acclist.id
                accid1 = int(accid)
                aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                if aapays:
                   accdatas.append(aapays)
                   msg = 3
                if not aapays:
                   msg = 4
            idatas = []
            for ilist in res:
                aid = ilist.id
                apid = int(aid)
                idata = http.request.env['x_interview'].sudo().search(['&','&',('x_applicant_id','=',apid),('x_type','=',1),('x_status','=',1)])
                if idata:
                   idatas.append(idata)
                   msg = 3
                if not idata:
                   msg = 4
            if res:
                return http.request.render('website.acceptance-lists-search', {
                # pass company details to the webpage in a variable
                'testlist': res,'pager': pager,'now':now,'name':name,'jname':jname,'jid':jid ,'state':state,'start':start,'end':end,'accdatas':accdatas,'idatas':idatas,'msg':msg,'start':start,'end':end,'daterange':daterange})
            if not res:
                a = ()
                return http.request.render('website.acceptance-lists-search', {
                # pass company details to the webpage in a variable
                'testlist': a,'jid':jid,'start':start,'end':end,'state':state,'name':name,'jname':jname})

    @http.route(['/my-registration-list1/','/my-registration-list1/page/<int:page>/'],type='http', auth='public', website=True)
    def myreglist(self, page=1,**kw):
          # YOUR VARIABLE value_input SHOULD BE AVAILABLE IN THE QUERY STRING
          #query_string = request.httprequest.query_string
          now = fields.Datetime.now().date()
          name = post.get('name')
          jid = post.get('jid')
          state = kw.get('stateid')
          if jid:
             testid = int(jid)
          if not jid:
             return json.dumps({'status':500, 'message':_("JobID is null")})
          stateid = int(state)
          name_lower = kw.get('name').lower()
          name_upper =kw.get('name').upper()
          com_name = http.request.env['hr.applicant'].sudo().search([])
          if com_name:
              res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',testid),'|','|','|','|','|','|','|','|',('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
              total = http.request.env['hr.applicant'].sudo().search_count(['|','|','|','|','|','|','|','|',('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
              #query = "select * from blog.post where name LIKE '%name%'"
              #request.cr.execute(query)
              #res = request.cr.fetchall()
              pager = request.website.pager(
                   url='/my-registration-list1',
                   url_args= kw,
                   total=total,
                   page=page,
                   step=20,
                   scope=5,
              )
              if res:
                  return http.request.render('website.my-registration-list1', {
                  # pass company details to the webpage in a variable
                  'name': res,'pager': pager,'now':now,'sresult':name ,'jid':jid ,'testid':testid,'state':state, 'stateid':stateid})

              if not res:
                  a = ()
                  return http.request.render('website.my-registration-list1', {
                  # pass company details to the webpage in a variable
                  'name': a,'sresult':name, 'jid':jid})

    @http.route(['/rleregistrationformdetail'], type='http', auth='public', website=True)
    def rle_datail(self, **kw):
          pid = kw.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.rlecregistrationformupdate', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})


    @http.route(['/rfperegistrationformdetail'], type='http', auth='public', website=True)
    def rfpe_datail(self, **kw):
          pid = kw.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.rfperegistrationformupdate', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route(['/rlperegistrationformdetail'], type='http', auth='public', website=True)
    def rlpe_datail(self, **kw):
          pid = kw.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.rlperegistrationformupdate', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route(['/acperegistrationformdetail'], type='http', auth='public', website=True)
    def acpe_datail(self, **kw):
          pid = kw.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.previous-acpe-registration', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route(['/rgtcregistrationformdetail'], type='http', auth='public', website=True)
    def rgtc_datail(self, **kw):
        pid = kw.get('id')
        par_id = request.env.user.partner_id.id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aid = int(pid)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.rgtcregistrationform', {'rgtcdata': rtcdata, 'fdate':fdate,'edate':edate,'todaydate':todaydate,'ddata': ddata,'paystatus':paystatus,'paydata':paydata,'form_type':form_type,'academicfiles':academicfiles,'nrc':nrc,'nrcmm':nrcmm})


    @http.route(['/rtcregistrationformdetail'], type='http', auth='public', website=True)
    def rtc_datail(self, **kw):
        pid = kw.get('id')
        par_id = request.env.user.partner_id.id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aid = int(pid)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.rtcregistrationform', {'rtcdata': rtcdata, 'fdate':fdate,'edate':edate,'todaydate':todaydate,'ddata': ddata,'paydata':paydata,'aapay':aapay,'form_type':form_type,'paystatus':paystatus,'academicfiles':academicfiles,'nrc':nrc,'nrcmm':nrcmm})

    @http.route(['/recregistrationformdetail'], type='http', auth='public', website=True)
    def rec_datail(self, **kw):
          pid = kw.get('id')
          pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
          ddata = http.request.env['x_discipline'].sudo().search([])
          nrc = http.request.env['x_nrclist'].sudo().search([],)
          nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
          return http.request.render('website.recregistrationform', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route(['/agtechregistrationformdetail'], type='http', auth='public', website=True)
    def agtech_datail(self, **kw):
        pid = kw.get('id')
        par_id = request.env.user.partner_id.id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aid = int(pid)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        #fdate = new Date(fdate1)
        return http.request.render('website.agtechregistrationform', {'rtcdata': rtcdata,'fdate':fdate,'edate':edate,'todaydate':todaydate,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'paydata':paydata,'aapay':aapay,'form_type':form_type,'paystatus':paystatus,'academicfiles':academicfiles})

    @http.route(['/atechregistrationformdetail'], type='http', auth='public', website=True)
    def atech_datail(self, **kw):
        pid = kw.get('id')
        par_id = request.env.user.partner_id.id
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
       # anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aid = int(pid)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.atechregistrationform', {'pdata': pdata, 'fdate':fdate,'edate':edate,'todaydate':todaydate,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'aapay':aapay,'form_type':form_type,'paystatus':paystatus,'academicfiles':academicfiles,'paydata':paydata})

    @http.route('/aecregistrationformdetail', type='http', auth="public",method='POST', website=True)
    def aec_detail(self, **kw):
        id = kw.get('id')
        par_id = request.env.user.partner_id.id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search([('x_partner','=',par_id)])
        jid1 = rtcdata.job_id
        jid = int(jid1) 
        apaydata = http.request.env['x_application_payment'].sudo().search(['&',('x_application_id','=',jid),('x_payment_id','=',1)])
        apayid1 = apaydata.id
        apayid = int(apayid1)
        aid = int(id)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.aecregistrationform',{'rtcdata':rtcdata,'fdate':fdate,'edate':edate,'todaydate':todaydate,'ddata':ddata,'nrc':nrc,'nrcmm':nrcmm,'aapay':aapay,'form_type':form_type,'paystatus':paystatus,'academicfiles':academicfiles,'paydata':paydata})


    @http.route('/rserenewalformupdate1', type='http', auth='public', website=True, method=['POST'])
    def rserenewalupdate1(self, **post):
        #  pid = kw.get('id')
        peid = post.get('id')      
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = pdata.x_photo
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = pdata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = pdata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = pdata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = pdata.x_nrc_photo_back_name
        if post.get('x_firstdegree_attachment'):
           FileStorage = post.get('x_firstdegree_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_firstdegree_attachment = base64.encodestring(FileData)
        if not post.get('x_firstdegree_attachment'):
           x_firstdegree_attachment = pdata.x_firstdegree_attachment
        if post.get('x_firstdegree_filename'):
           x_firstdegree_filename = post.get('x_firstdegree_filename')
        if not post.get('x_firstdegree_filename'):
           x_firstdegree_filename = pdata.x_firstdegree_filename
        Job = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        if Job:
            val = {
                    'x_state':2,
                    'x_reg_no':post.get('x_reg_no'),
                    'x_dob':post.get('x_dob'),
                   # 'x_name_mm':post.get('x_name_mm'),
                    'x_nrc_no_en':post.get('x_nrc_no_en'),
                    'partner_name':post.get('partner_name'),
                    'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                    'x_address_en':post.get('x_address_en'),
                    'x_address_mm':post.get('x_address_mm'),
                    'partner_phone':post.get('partner_phone'),
                    'x_nrc_photo_front':x_nrc_photo_front,
                    'x_nrc_photo_front_name':x_nrc_photo_front_name,
                    'x_nrc_photo_back':x_nrc_photo_back,
                    'x_nrc_photo_back_name':x_nrc_photo_back_name,
                    'x_photo':x_photo,
                    'partner_id':post.get('partner_id'),
                    'x_city_state':post.get('x_city_state'),
                    'x_township':post.get('x_township'),
                    'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                    'x_firstdegree_attachment':x_firstdegree_attachment,
                    'x_firstdegree_filename':x_firstdegree_filename
                  }
        Job.sudo().write(val)
        type = 'RSERENEWAL'
        return http.request.render('website_hr_recruitment.thankyou', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'type':type})

    @http.route('/rserenewalformupdate', type='http', auth='public', website=True, method=['POST'])
    def rse_renewal_update(self, **post):
       # pid = kw.get('id')
        peid = request.website._website_form_last_record().sudo().id
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        return http.request.render('website.rse-renewal', {'pdata':pdata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route(['/rse-renewal'], type='http', auth='public', website=True)
    def rse_renewal_data(self, **kw):
        pid = kw.get('id')
        peid = request.website._website_form_last_record().sudo().id
        #pdata = http.request.env['hr.applicant'].sudo().search([('id','=',peid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
          #disdata = http.request.env['x_hr_applicant_x_discipline_rel'].sudo().search([('hr_applicant_id','=',pid)])
        return http.request.render('website.rse-renewal', {'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/previousrserenewal', type='http', auth='public', website=True, method='POST')
    def previous_rse_renewal(self, **kw):
        pid = kw.get('id')
        predata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        type = 'RSERENEWAL'
        return http.request.render('website.reviewregistrationform', {'type':type,'predata':predata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/reviewregistrationform', type='http', auth='public', website=True, method='POST')
    def single_view(self, **kw):
        aid = kw.get('id')
        userid = request.env.user.partner_id.id
        jid = kw.get('jid')
        pedata = http.request.env['hr.applicant'].sudo().search(['&',('partner_id','=',userid),('id','=',aid)])
       # pedatas = http.request.env['hr.applicant'].sudo().search([('partner_id','=',userid)])
       # pdatas = [] 
       # for peid in pedatas:
       #     aid = peid.id
       #     pe = http.request.env['hr.applicant'].sudo().search(['&',('partner_id','=',userid),'|',('x_state','=',2),('x_state','=',4)])
       #     pdatas.append(pe)
        sdata = http.request.env['hr.applicant'].sudo().search(['&',('id','=',aid),'|',('x_state','=',1),('x_state','=',2)])
       # predata = http.request.env['hr.applicant'].sudo().search(['&',('id','=',aid),'|',('x_state','=',2),('x_state','=',4)])
        predata = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        careerfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pedata.id),('res_model','=','hr.applicant'),('x_field','=','x_career')])
        programfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pedata.id),('res_model','=','hr.applicant'),('x_field','=','x_program')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pedata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        anotherfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pedata.id),('res_model','=','hr.applicant'),('x_field','=','x_another')])
        if sdata:
           return http.request.render('website.saveform', {'userid':userid, 'sdata':sdata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'careerfiles':careerfiles,'programfiles':programfiles,'academicfiles':academicfiles,'anotherfiles':anotherfiles})
           #return http.request.render('website.saveform', {'userid':userid, 'sdata':sdata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,})
        if predata:
           return http.request.render('website.reviewregistrationform', {'userid':userid, 'predata':predata,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'careerfiles':careerfiles,'programfiles':programfiles,'academicfiles':academicfiles,'anotherfiles':anotherfiles})
           #return http.request.render('website.reviewregistrationform', {'userid':userid, 'preddata':pdatas,'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/save_application_payment/', type='http', auth="public", methods=['POST'], website=True)
    def save_application_payment(self, **post):
        id = post.get('id')
        userid = request.env.user.partner_id.id
        Pay = http.request.env['x_application_payment']
        Pay1 = http.request.env['x_application_payment'].sudo().search([('id','=',id)])
        app_id=post.get('x_application_id')
        appid=int(app_id)
        pay_id=post.get('x_payment_id')  
        payid=int(pay_id)
        fine = post.get('x_fine')
        finefee = post.get('x_amount')
        if fine and finefee:
           fee = float(0.5)
           fine_fee = fee * float(finefee)
        if not fine:
           fine_fee = 0.0
        paydata = http.request.env['x_application_payment'].sudo().search(['&',('x_application_id','=',appid),('x_payment_id','=',payid)])
        paymentdata = http.request.env['x_payment_type'].sudo().search([('x_form_type','=','Second')])
        val = {    'x_name':post.get('x_name'),
                   'x_payment_type':post.get('x_payment_type'),
                   'x_amount':post.get('x_amount'),
                   'x_payment_id':post.get('x_payment_id'),
                   'x_application_id':post.get('x_application_id'),
                   'x_type':post.get('x_type'),
                   'x_status':2,
                   'x_partner':userid,
                   'x_currency':post.get('x_currency'),
                   'x_fine_fee': fine_fee,
                   'x_fine': fine,
                 }
        if id:
           Pay1.sudo().write(val)
           return request.redirect('/application-payment-records')
        if not id:
           if not paydata:
              Pay.sudo().create(val)  
           if paydata:
              msg='This type of payment is already exists.'
           name=post.get('x_name')
           applicationid=post.get('x_application_id')
           amount=post.get('x_amount')
           partner=post.get('x_partner')
           paytype=post.get('x_payment_id')
           type=post.get('x_type')
           currency=post.get('x_currency')
           paymenttype=post.get('x_payment_type')
           lid = http.request.env['x_application_payment'].sudo().search([], order="id desc", limit=1)
           msg=''
           return http.request.render('website.application-payment',{'lid':lid, 'paydata':paymentdata, 'x_name':name, 'x_application_id':applicationid, 'x_amount':amount, 'x_partner':partner, 'x_payment_id':paytype, 'x_type':type, 'x_currency':currency, 'x_payment_type':paymenttype, 'msg':msg})


    @http.route('/application-payment', type='http', auth="public", website=True)
    def app_payment(self, **kw):
        lid = http.request.env['x_application_payment'].sudo().search([], order="id desc", limit=1)  
        paydata = http.request.env['x_payment_type'].sudo().search([('x_form_type','=','Second')])
        #retPay1 = http.request.env['x_application_payment'].sudo().search([('id','=',id)])
        #Pay1 = http.request.env['x_application_payment'].sudo().search([('id','=',id)])
        job_data = http.request.env['hr.job'].sudo().search(['&','&','&',('id','!=',13),('id','!=',14),('id','!=',16),('id','!=',29)])
        return http.request.render('website.application-payment',{'paydata':paydata, 'lid':lid,'job_data':job_data})
 
    @http.route('/accept_form2', type='http', auth="public", methods=['POST'], website=True)
    def accept_form_second(self, **post):
        Pay = http.request.env['x_applicant_application_payment']
        applicant_id = post.get('id')
        application_id = post.get('job_id')
        date =  fields.Datetime.now()
        aid = int(applicant_id)
        form_type = post.get('x_form_type')
        jid = int(application_id)
        fid = int(form_type)
        #apno_lid = http.request.env['hr.applicant'].sudo().search([('job_id','=',jid)], order="x_approval_no desc", limit=1)
        #if not apno_lid.x_approval_no:
         #  approval_no = apno_lid.job_id.name+'00001'
        #if apno_lid.x_approval_no:
         #  str_no = apno_lid.x_approval_no
         #  str_num = strno[-5:]
         #  num = int(str_num)+1
         #  no = '{:05d}'.format(num)
         #  approval_no = apno_lif.job_id.name+no
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
        apayid1 = apay.id
        apayid = int(apayid1)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',aid),('x_application_payment_id','=',apayid)])
        if aapay:
           msg = 1
           job_type = post.get('job_type')
           testlist = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)])
           raise ValidationError("Already Paid.")
           #return http.request.redirect('/my-registration-list?name='+type)
           #return http.request.render('website.my-registration-list1',{'msg':msg,'testlist':testlist})
        if not aapay:
           adata = http.request.env['hr.applicant'].sudo().search([('id','=',applicant_id)])
           status1 = adata.x_form_status
           status = int(status1)
           form_type1 = int(form_type)
           if form_type1 == sum([status,1]):
              res = 'True'
              result = sum([status,1])
              Pay = http.request.env['x_applicant_application_payment']
              apno_lid = http.request.env['hr.applicant'].sudo().search(['&',('x_approval_no','!=',''),('job_id','=',jid)], order="x_approval_no desc", limit=1)
              if not apno_lid.x_approval_no:
                 approval_no = adata.job_id.name+'00001'
              if apno_lid.x_approval_no:
                 str_no = apno_lid.x_approval_no
                 str_num = str_no[-5:]
                 num = int(str_num)+1
                 no = '{:05d}'.format(num)
                 approval_no = apno_lid.job_id.name+no
              Applicant = http.request.env['hr.applicant'].sudo().search([('id','=',applicant_id)])
              val = {
                      'x_applicant_id': applicant_id,
                      'x_payment_status': 'Pending',
                      'x_application_payment_id': apay.id,
                      'x_apply_date': date,
                      'x_remark':post.get('x_remark'),
                      'x_job_id': Applicant.job_id.id,
                      'x_partner_id': Applicant.partner_id.id,
                    }
              value = {
                        'x_state':5,
                        'x_form_status':5,
                        'x_accepted_date': fields.Datetime.now(),
                        'x_approval_no': approval_no,
                      }
              Pay.sudo().create(val)
              Applicant.sudo().write(value)
              job_id = Applicant.job_id.id
              history = http.request.env['x_history'].sudo().search([])
              hvalue = { 'x_state':'5', 'x_applicant_id': applicant_id,'x_job_id': job_id }
              history.sudo().create(hvalue)
              hid = str(applicant_id)
              aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',aid),('x_application_payment_id','=',apayid)])
              aaid = aapay.id
              aaid1 = str(aaid)
              job_type = Applicant.job_id.name
              useremail = Applicant.email_from
              adminemail = "mecportal20@gmail.com"
              datemail = fields.Datetime.now().strftime('%B %d')
              #datemail = str(datemail1)
              subject = "Form accept"
              subjectmail = " "
              username = Applicant.partner_name
              jobname = Applicant.job_id.name
              pre_code_no = Applicant.x_reg_no
              form_type_name1 = apay.x_amount
              form_type_name2 = int(form_type_name1)
              form_type_amount = str(form_type_name2)
              form_type_name = apay.x_name
              dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
              durl = dynamic_url.x_name
              regbranch = "(01-2316995 / 01-2316891)"
              textaccept = "<p><span>Data Valid.</span><br><span>Please take payment Kyat "+form_type_amount+"/- for "+jobname+" Application Fees,and from type is "+form_type_name+"</span><br><span>by Your "+jobname+" Application Pre Code No. "+pre_code_no+"</span><br><span>and your approval no "+approval_no+" your payment link - "+durl+aaid1+"</span></p>"
              message = "<table><tbody><tr><td><span>Dear "+username+"</span>"+textaccept+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
             # message = "Your registration for apprentice engineer certificate with reg no "+job_type+"-"+hid+" has been applied and your payment link- http://40.68.26.236/payment?aaid="+aaid1
              y = send_email(useremail,message,subject)
              url= jobname.lower()+'-registration-list'
              if y["state"]:
                 return http.request.redirect(url)
                 #return http.request.render('website.testpayment',{'form_type':form_type,'aapay':aapay,'apay':apay,'status':status,'result':result,'res':useremail})
              if not y["state"]:
                 return http.request.redirect('/home')
           if not form_type1 == sum([status,1]):
              return http.request.redirect('/home')
              #return http.request.render('website.testpayment',{'form_type':form_type,'aapay':aapay,'apay':apay,'status':status,'result':result,'res':res})

    @http.route('/accept_form_card', type='http', auth="public", methods=['POST'], website=True)
    def accept_form_cardfee(self, **post):
        applicant_id = post.get('id')
        application_id = post.get('job_id')
        aid = int(applicant_id)
        form_type = post.get('card_form_type')
        jid = int(application_id)
        fid = int(form_type)
        date =  fields.Datetime.now()
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
        apayid2 = apay.id
        apayid1 = int(apayid2)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',aid),('x_application_payment_id','=',apayid1)])
        if aapay:
           msg = 1
           job_type = post.get('job_type')
           testlist = http.request.env['hr.applicant'].sudo().search([('job_id','=',12)])
           raise ValidationError("Already Paid.")
        if not aapay:
           Pay = http.request.env['x_applicant_application_payment']
           apno_lid = http.request.env['hr.applicant'].sudo().search(['&',('x_approval_no','!=',''),('job_id','=',jid)], order="x_approval_no desc", limit=1)
           Applicant = http.request.env['hr.applicant'].sudo().search([('id','=',applicant_id)])
           val ={
                 'x_applicant_id': applicant_id,
	   	 'x_payment_status': 'Pending',
	   	 'x_application_payment_id': apay.id,
	   	 'x_apply_date': date,
	   	 'x_remark':post.get('card_remark'),
	   	 'x_job_id': Applicant.job_id.id,
	   	 'x_partner_id': Applicant.partner_id.id,
                  }
           value ={
                   'x_state':26,
                  }
           Pay.sudo().create(val)
           Applicant.sudo().write(value)
           job_id = Applicant.job_id.id
           aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',Applicant.id),('x_application_payment_id','=',apay.id)])
           aaid = aapay.id
           aaid1 = str(aaid)
           job_type = Applicant.job_id.name
           useremail = Applicant.email_from
           adminemail = "mecportal20@gmail.com"
           datemail = fields.Datetime.now().strftime('%B %d')
           #datemail = str(datemail1)
           subject = "Generate Card"
           subjectmail = " "
           username = Applicant.partner_name
           jobname = Applicant.job_id.name
           approval_no = Applicant.x_approval_no
           pre_code_no = Applicant.x_reg_no
           form_type_name1 = apay.x_amount
           form_type_name2 = int(form_type_name1)
           form_type_amount = str(form_type_name2)
           form_type_name = apay.x_name
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           durl = dynamic_url.x_name
           regbranch = "(01-2316995 / 01-2316891)"
           textaccept = "<p><span>Data Valid.</span><br><span>Please take payment Kyat "+form_type_amount+"/- for "+jobname+" Card Fees,and from type is "+form_type_name+"</span><br><span>by Your "+jobname+" Application Pre Code No. "+pre_code_no+"</span><br><span>and your approval no "+approval_no+" your payment link - "+durl+aaid1+"</span></p>"
           message = "<table><tbody><tr><td><span>Dear "+username+"</span>"+textaccept+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
           # message = "Your registration for apprentice engineer certificate with reg no "+job_type+"-"+hid+" has been applied and your payment link- http://40.68.26.236/payment?aaid="+aaid1
           y = send_email(useremail,message,subject)
           url= jobname.lower()+'-registration-list'
           if y["state"]:
              return http.request.redirect(url)
              #return http.request.render('website.testpayment',{'form_type':form_type,'aapay':aapay,'apay':apay,'status':status,'result':result,'res':useremail})
           if not y["state"]:
              return http.request.redirect('/home')

    @http.route('/ttest', auth="public", method=['POST'], website=True)
    def testforsearch2(self,**post):
        return http.request.render('website.my-registration-list')

    @http.route('/proceed-payment', type='http', auth="public", method='POST', website=True)
    def login_checking(self, **kw):
         id = kw.get('aaid')
         aid = int(id)
         aapay = http.request.env['x_applicant_application_payment'].sudo().search([('id','=',aid)])
         aapid = aapay.x_applicant_id.partner_id.id
         pid = request.env.user.partner_id.id
         #if aapid == pid:
            #return http.request.redirect('/payment?aaid='+id)
         if not pid == 3:
            if aapid == pid:
               return http.request.redirect('/payment?aaid='+id)
            if not aapid == pid:
               return http.request.redirect('/home')
               #return http.request.render('website.testpayment',{'aapid':aapid,'pid':pid})
         if pid == 3:
            if not aapid == pid:
               return http.request.render('web.login',{'aaid':aapay})

    @http.route('/payment', type='http', auth="public", method='POST', website=True)
    def payment(self, **kw):
        id = kw.get('aaid')
        aaid = int(id)
        pid = request.env.user.partner_id.id
        #adatas = http.request.env['hr.applicant'].sudo().search([('partner_id','=',pid)])
        #adata = http.request.env['hr.applicant'].sudo().search([('partner_id','=',pid)])
       # apid = adata.id
        aapay1 = http.request.env['x_applicant_application_payment'].sudo().search([('id','=',aaid)])
        aapid = aapay1.x_applicant_id.partner_id.id
        #test = []
        #aapays = []
        #apayids = []
        #testapays = []
        #testpays = []
        #for adata in adatas:
            #aid = adata.id
            #test.append(aid)
            #aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
            #aapays.append(aapay)
            #apayid = aapay.x_application_payment_id
            #apayids.append(apayid)
            #testapay = http.request.env['x_application_payment'].sudo().search([('id','=',aapay['x_application_payment_id'].id)])
            #testapays.append(testapay)
            #testpay = http.request.env['x_payment_type'].sudo().search([('id','=',testapay['x_payment_id'].id)])
            #testpays.append(testpay)
        if pid == aapid:
           return http.request.render('website.payment-type', {'aapay':aapay1,'aaid':aaid})
        if not pid == aapid:
           aapid = aapay.x_applicant_id.partner_id.id
           #return http.request.render('website.testpayment',{'aapid':aapid,'pid':pid})
           return http.request.redirect('/home')

    @http.route(['/payment_type'], type='http', auth='public', website=True, csrf=False, methods=['POST'])
    def _test(self, **post):
        #aaid = post.get('id')
        #aid = post.get('x_applicant_id')
        pay_value = post.get('payment')
        headers = {'content-type': 'application/json'}
        appID = post.get('appID')
        usersyskey = post.get('usersyskey')
        name = post.get('name')
        street = post.get('street')
        city = post.get('city')
        email = post.get('email')
        partner = request.env.user.partner_id
        userid = partner.id
        eventID = post.get('eventID')
        #pay_value = post.get('payment')
        total = post.get('total')
        #currency = post.get('currency')
        res_url1 = "http://13.76.228.243:8080/paymentservice/result.jsp"
        res_url2 = "http://13.76.228.243:8080/paymentservice/back.jsp"
        refcode = post.get('refcode')
        datas = {
                 "appID": appID,
                 "usersyskey": usersyskey,
                 "name": name,
                 "street": "teststreet",
                 "city": "testcity",
                 "user_defined_1": email,
                 "user_defined_2": "018",
                 "email" : email,
                 "orderid": "",
                 "t5":"031302734996EDCA085E74631C3D6DC1E0A422C83FCCBE15F9A0E39F0E96DB98",
                 "version":"8.5",
                 "merchant_id":"104104000000437",
                 "payment_description":"MIT",
                 "pmethod": pay_value,
                 "eventID": eventID,
                 "total": total,
                 "currency1": 104,
                 "devicestatus" : "web",
                 "refcode": refcode,
                 "amount":total,
                 "customer_email": email,
                 "result_url_1": res_url1,
                 "result_url_2": res_url2,
                 "hash_value":"",
                }

        #encData = self.encode_data(datas)
        #headers = {'content-type': 'application/json', 'Authen-Token': encData}
        #pdata = {
        #         "eData" : "!!!",
        #        }
        url = "http://13.76.228.243:8080/paymentservice/module001/servicePayment/savePayment"
        response = requests.post(url, data=json.dumps(datas), headers=headers)
        y = response.json()
        return request.redirect(y["url"])

    def encode_data(self, payload):
        secretKey = "f815f59b9fde0863ced32a0d313d45370f6cdfc2def08b12"
        encoded_jwt = jwt.encode(payload,secretKey, algorithm='HS256')
        return encoded_jwt

 
    @http.route('/save_payment', type='http', auth="public", website=True)
    def save_payment(self, **post):
        aaid = post.get('id')
        aid = post.get('x_applicant_id')
        pay_value = post.get('payment')
        headers = {'content-type': 'application/json'}
        appID = '018'
        usersyskey = post.get('usersyskey')
        name = post.get('name')
        street = post.get('street')
        city = post.get('city')
        email = post.get('email')
        partner = request.env.user.partner_id
        userid = partner.id
        eventID = post.get('id')
        pay_value = post.get('payment')
        total = post.get('x_amount')
        #currency = post.get('currency')
        refcode = post.get('refcode')
        datas = {
                 "appID": appID,
                 "usersyskey": usersyskey,
                 "name": name,
                 "street": street,
                 "city": city,
                 "user_defined_1": email,
                 "user_defined_2": "018",
                 "email" : email,
                 "t5":"F90E04C29260A1E67F02B39A533A95459ACC0631B69213FFDB08ACD2C147A4B2",
                 "version":"8.5",
                 "merchant_id":"104104000000437",
                 "payment_description":"MIT",
                 "pmethod": pay_value,
                 "eventID": eventID,
                 "total": total,
                 "currency1": 104,
                 "devicestatus" : "web",
                 "refcode": refcode,
                 "amount":total,
                 "customer_email": email,
                 "result_url_1":"https://uat-paymentgateway.mitcloud.com/paymentservice/result.jsp",
                 "result_url_2":"https://uat-paymentgateway.mitcloud.com/paymentservice/back.jsp",
                 "hash_value":"",
                } 
        url = "https://uat-paymentgateway.mitcloud.com/paymentservice/module001/servicePayment/savePayment"
        response = requests.post(url, data=json.dumps(datas), headers=headers)
        y = response.json()
        return request.redirect(y["url"])
        #adata = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
        #email = adata.email_from
        #message = "Payment Successful"
        #aapay = http.request.env['x_applicant_application_payment'].sudo().search([('id','=',aaid)])
        #val = {
         #       'x_payment_status':'Payment'
         #     }
        #aapay.sudo().write(val)
        #y = send_email(email,message)
        #if y["state"]:
        #   return http.request.render('website.thank-you-for-payment',{'aid':email})
        #if not y["state"]:
        #   return request.redirect('/home')
     
    @http.route('/mpu_update', type='http', auth='public', website=True, csrf=False)
    def mpu_ret(self, **post):
        appID = '018'
        version = post.get('version')
        request_timestamp = post.get('request_timestamp')
        merchant_id = post.get('merchant_id')
        currency = post.get('currency')
        order_id = post.get('order_id')
        amount = post.get('amount')
#        invoice_no = post.get('invoice_no')
        transaction_ref = post.get('transaction_ref')
        approval_code = post.get('approval_code')
        eci = post.get('eci')
        transaction_datetime = post.get('transaction_datetime')
        payment_channel = post.get('payment_channel')
        payment_status = post.get('payment_status')
        channel_response_code = post.get('channel_response_code')
        channel_response_desc = post.get('channel_response_desc')
        masked_pan = post.get('masked_pan')
#        stored_card_unique_id = post.get('stored_card_unique_id')
        backend_invoice = post.get('backend_invoice')
#        paid_channel = post.get('paid_channel')
#        recurring_unique_id = post.get('recurring_unique_id')
#        paid_agent = post.get('paid_agent')
        payment_scheme = post.get('payment_scheme')
        user_defined_1 = post.get('user_defined_1')
        user_defined_2 = post.get('user_defined_2')
#        user_defined_3 = post.get('user_defined_3')
#        user_defined_4 = post.get('user_defined_4')
#        user_defined_5 = post.get('user_defined_5')
#        browser_info = post.get('browser_info')
#        ippPeriod = post.get('ippPeriod')
#        ippInterestType = post.get('ippInterestType')
        ippInterestRate = post.get('ippInterestRate')
        ippMerchantAbsorbRate = post.get('ippMerchantAbsorbRate')
        process_by = post.get('process_by')
#        sub_merchant_list = post.get('sub_merchant_list')
        hash_value = post.get('hash_value')
        #headers = {'content-type': 'application/json'}
        datas = {
                "appID": appID,
                "version":version,
                "request_timestamp":request_timestamp,
                "merchant_id":merchant_id,
                "currency": currency,
                "order_id": order_id,
                "amount" : amount,
                "invoice_no" : "",
                "transaction_ref" : transaction_ref,
                "approval_code" : approval_code,
                "eci" : eci,
                "transaction_datetime" : transaction_datetime,
                "payment_channel" : payment_channel,
                "payment_status" : payment_status,
                "channel_response_code" : channel_response_code,
                "channel_response_desc" : channel_response_desc,
                "masked_pan" : masked_pan,
                "stored_card_unique_id" : "",
                "backend_invoice" : backend_invoice,
                "paid_channel" : "",
                "recurring_unique_id" : "",
                "paid_agent" : "",
                "payment_scheme" : payment_scheme,
                "user_defined_1" : user_defined_1,
                "user_defined_2" : user_defined_2,
                "user_defined_3" : "",
                "user_defined_4" : "",
                "user_defined_5" : "",
                "browser_info" : "",
                "ippPeriod" : "",
                "ippInterestType" : "",
                "ippInterestRate" : ippInterestRate,
                "ippMerchantAbsorbRate" : ippMerchantAbsorbRate,
                "process_by" : process_by,
                "sub_merchant_list" : "",
                "hash_value" : hash_value,
                "skey" : "031302734996EDCA085E74631C3D6DC1E0A422C83FCCBE15F9A0E39F0E96DB98"
                }
        encData = self.encode_data(datas)
        headers = {'content-type': 'application/json', 'Authen-Token': encData}
        pdata = {
                 "eData" : "!!!",
                }
        url = "http://13.76.228.243:8080/paymentservice/module001/servicePayment/mpuupdate"
        response = requests.post(url, data=json.dumps(pdata), headers=headers)
        y = response.json()
        if y["state"]:
            return request.redirect(y["url"])

    @http.route(['/application-payment-records','/application-payment-records/page/<int:page>'], type='http', auth="public", website=True)
    def application_paymentrecord(self, page=1):
        jobdata = http.request.env['hr.job'].sudo().search(['&','&','&',('id','!=',13),('id','!=',14),('id','!=',16),('id','!=',29)])
        position = 'all' 
        aprecords = http.request.env['x_application_payment'].sudo().search([('x_amount','!=',0)],offset=(page-1) * 15, limit=15)
        #accre = http.request.env['ir.attachment'].sudo().search([('x_category','=','Accreditation')],offset=(page-1) * 6, limit=6)
        total = http.request.env['x_application_payment'].sudo().search_count([('x_amount','!=',0)])
        pager = request.website.pager(
             url='/application-payment-records',
             total=total,
             page=page,
             step=15,
             scope=4,
        )
        return http.request.render('website.application-payment-records',{'aprecords':aprecords,'pager':pager, 'jobdata':jobdata})

    @http.route('/applicationpaymentdetail',  type='http', auth="public", website=True)
    def application_paymentdetail(self, **kw):
        apid = kw.get('id')
        aprecords = http.request.env['x_application_payment'].sudo().search([('id','=',apid)])
        job_data = http.request.env['hr.job'].sudo().search(['&','&','&',('id','!=',13),('id','!=',14),('id','!=',16),('id','!=',29)])
        return http.request.render('website.application-payment',{'aprecords':aprecords,'job_data':job_data})

    @http.route('/applicant-application-payment-records',  type='http', auth="public", website=True)
    def aapay_record(self, **kw):
        aaprecords = http.request.env['x_applicant_application_payment'].sudo().search([])
        return http.request.render('website.applicant-application-payment-records',{'aaprecords':aaprecords})

    @http.route('/aapaydetail',  type='http', auth="public", website=True)
    def aapay_detail(self, **kw):
        aapid = kw.get('id')
        aaprecords = http.request.env['x_applicant_application_payment'].sudo().search([('id','=',aapid)])
        return http.request.render('website.applicant-application-payment',{'aaprecords':aaprecords})

    @http.route('/reviewtest', type='http', auth='public', website=True, method='POST')
    def review_test(self, **kw):
        pid = kw.get('id')
        userid = request.env.user.partner_id.id
        pedatas = http.request.env['hr.applicant'].sudo().search([('partner_id','=',userid)])
        pdatas = []
        for peid in pedatas:
            aid = peid.id
            pe = http.request.env['hr.applicant'].sudo().search(['&',('partner_id','=',userid),'|',('x_state','=',2),('x_state','=',4)])
            pdatas.append(pe)
        return http.request.render('website.reviewtest',{'pdatas':pdatas,'pedatas':pedatas})

    @http.route('/delete_application_payment/', type='http', auth="public", methods=['POST'], website=True)
    def delete_application_payment(self, **post):
        id = post.get('id')
        Pay = http.request.env['x_application_payment'].sudo().search([('id','=',id)])
        val = {
                'x_status':4
              }
        Pay.sudo().write(val)
        msg = 4
        aprecords = http.request.env['x_application_payment'].sudo().search([])
        return http.request.render('website.application-payment-records', {'msg':msg,'aprecords':aprecords})

    @http.route('/thank-you-for-payment', type='http', auth="public", method='POST', website=True)
    def thank_payment(self, **kw):
        order_id = kw.get('order_id')
        #payment = http.request.env['x_payment'].sudo().search([('x_paymentno','=',sid)])
        o_id = int(order_id)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('id','=',o_id)])
        val = {
                'x_payment_status':'Paid'
               }
        aapay.sudo().write(val)
        aid = aapay.x_applicant_id.id
        Applicant = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
        useremail = Applicant.email_from
        adminemail = "mecportal20@gmail.com"
        datemail = fields.Datetime.now().strftime('%B %d')
        subject = "Success Payment"
        subjectmail = " "
        username = Applicant.partner_name
        jobname = Applicant.job_id.name
        regno = Applicant.x_reg_no
        regbranch = "(01-2316995 / 01-2316891)"
        textaccept = "<p><span>Thank you for the registration. Your application process is successful.</span><br><span>Your "+jobname+" Application No. – "+regno+"</span></p>"
        message = "<table><tbody><tr><td><span>Dear "+username+"</span>"+textaccept+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
        y = send_email(useremail,message,subject)
        return http.request.render('website.thank-you-for-payment',{'aaid':o_id,'aid':aid,'useremail':useremail,'Applicant':Applicant})

    @http.route(['/my-record','/my-record/page/<int:page>'], type='http', auth="public", website=True)
    def myrecord_list(self, page=1):
        val = request.env.user.partner_id.id
        reglists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)],offset=(page-1) * 20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count([('partner_id.id','=',val)])
        pager = request.website.pager(
                url='/my-record',
                total=total,
                page=page,
                step=20,
                scope=4,
        )
        tlists = []
        clists = []
        accdatas = []
        clist = []
        for reglist in reglists:
            aid = reglist.id
            tlist = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
            tlists.append(tlist)
            clist = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
            clists.append(clist)
            aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
            accdatas.append(aapays)
        if not clist:
           clist = ' '
        return http.request.render('website.my-record',{'reglists':reglists,'tlist':tlists,'clists':clists, 'clist':clist,'accdatas':accdatas,'pager':pager})

    @http.route('/testpayment', type='http', auth="public", method='POST', website=True)
    def test_payment(self, **kw):
        test = dir(self)
        return http.request.render('website.testpayment', {'test':test})


    @http.route('/confirmform/', type='http', auth="public", methods=['POST'], website=True)
    def confirm_form(self, **post):
        card = http.request.env['x_card']
        aid1 = post.get('id')
        aid = int(aid1)
        par_id = request.env.user.partner_id.id
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        type = post.get('job_type')
        ycount = post.get('year_count')
        year_count = int(ycount)
        date =  fields.Datetime.now()
        new_date1 = date + relativedelta(years=year_count)
        new_date = new_date1.date()
        val = {
                'x_card_reg_no':post.get('x_card_reg_no'),
                'x_applicant_id': post.get('id'),
                'x_application_id': post.get('job_id'),
                'x_start_date': date.date(),
                'x_expire_date': new_date,
                'x_total_year': year_count+1,
                'x_form_type': post.get('form_type'),
              }
        card.sudo().create(val)
        applicant = http.request.env['hr.applicant'].sudo().search(['&',('id','=',aid1),('x_state','=',6)])
        value = {
                  'x_state': 8
                }
        applicant.sudo().write(value)
        form_type = post.get('form_type')
        url = type.lower()+'_acceptance_list'
        return http.request.redirect(url)

    @http.route('/confirmform2/', type='http', auth="public", methods=['POST'], website=True)
    def confirm_form2(self, **post):
        card = http.request.env['x_card']
        aid1 = post.get('id')
        aid = int(aid1)
        par_id = request.env.user.partner_id.id
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        renew_aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_renew_status','=',True),('x_applicant_id','=',aid)])
        if renew_aapay:
           reval = {'x_renew_status':False}
           renew_aapay.sudo().write(reval)
        type = post.get('job_type')
        ycount = post.get('year_count')
        year_count = int(ycount)
        date =  fields.Datetime.now()
        new_date1 = date + relativedelta(years=year_count)
        new_date = new_date1.date()
        val = {
                'x_card_reg_no':post.get('x_card_reg_no'),
                'x_applicant_id': post.get('id'),
                'x_application_id': post.get('job_id'),
               # 'x_start_date': date.date(),
               # 'x_expire_date': new_date,
                'x_start_date': post.get('x_start_date'),
                'x_expire_date': post.get('x_expire_date'),
                'x_remark': post.get('x_confirm_remark'),
                'x_total_year': year_count+1,
                'x_form_type': post.get('form_type'),
              }
        res = card.sudo().create(val)
        applicant = http.request.env['hr.applicant'].sudo().search([('id','=',aid1)])
        jid = applicant.job_id.id
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'8', 'x_applicant_id': aid, 'x_job_id':jid }
        history.sudo().create(hvalue)
        #applicant = http.request.env['hr.applicant'].sudo().search(['&',('id','=',aid1), '|',('x_state','=',7),('x_state','=',13)])
        value = {
                  'x_state': 8
                }
        applicant.sudo().write(value)
        form_type = post.get('form_type')
        id = post.get('id')
        sid = str(id)
        card_id = post.get('x_card_reg_no')
        application_type = post.get('x_application_type')
        applicant_id = sid
        member_date = post.get('x_start_date')
        end_date = post.get('x_expire_date')
        #remark = post.get('x_remark')
        remark = post.get('x_confirm_remark')
        #if jid == 1:
        #if res:
        pdata = {
                 "card_id": card_id,
                 "application_type": application_type,
                 "applicant_id": applicant_id,
                 "member_date": member_date,
                 "end_date": end_date,
                 "remark": remark,
                }
        headers = {'content-type': 'application/json'}
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','blockchain')])
        url = dynamic_url.x_name
           #url = "http://13.76.253.98:8080/api/certificate"
        json_res = '1'
        url = type.lower()+'_acceptance_list'
        return http.request.redirect(url)
           #result = requests.post(url, data=json.dumps(pdata), headers=headers)
           #url = type.lower()+'-registration-list'
           #return http.request.redirect(url)
           #return http.request.redirect(/ltype+'-registration-list')
           #return http.request.redirect('/acceptance-lists?name='+type)
        #if not res:
           #return http.request.redirect('/home')

    @http.route('/final-list',  type='http', auth="public", website=True)
    def final_list(self, **kw):
        type=kw.get('name')
        val = request.env.user.partner_id.id
        return http.request.render('website.final-list',{'type':type})

    @http.route('/final-list-detail',  type='http', auth="public", website=True)
    def final_list_detail(self, **kw):
        type=kw.get('name')
        flists = http.request.env['x_card'].sudo().search([],order="write_date desc")
        return http.request.render('website.final-list-detail',{'flists':flists,'type':type})

    @http.route('/transfercmt', type='http', auth="public", methods=['POST'], website=True)
    def transfer_cmt(self, **post):
        id = post.get('id')
        pdata = request.env['hr.applicant'].sudo().search([('id','=',id)])
        if pdata:
           values = {
                     'x_state':7,
                     #'x_form_status':7,
                    }
           pdata.sudo().write(values)
           job_id = pdata.job_id.id
           history = http.request.env['x_history'].sudo().search([])
           hvalue = { 'x_state':'7', 'x_applicant_id': id, 'x_job_id':job_id }
           history.sudo().create(hvalue)
           type = pdata.job_id.name
           url = type.lower()+'-registration-list'
           return http.request.redirect(url)
           #return http.request.render('website.my-registration-list', {'type':type})

    @http.route('/detail_agtech', type='http', auth="public", website=True)
    def detail_view_agtech(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        agdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',agdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-agtech', {'rtcdata':agdata,'todaydate':todaydate,'fdate':fdate,'edate':edate,'aaprecords':aapay,'card':card,'paystatus':paystatus,'form_type':form_type,'academicfiles':academicfiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_atech', type='http', auth="public", website=True)
    def detail_view_atech(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        atdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',atdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-atech', {'pdata':atdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paystatus':paystatus,'form_type':form_type,'academicfiles':academicfiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm})


    @http.route('/detail_pe', type='http', auth="public", website=True)
    def detail_view_pe(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        prodata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',aid)])
        invodata = http.request.env['x_involve'].sudo().search([('x_applicant','=',aid)])
        sumdata = http.request.env['x_summary'].sudo().search([('x_applicant','=',aid)])
        verdata = http.request.env['x_verify'].sudo().search([('x_applicant','=',aid)])
        pedata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        township = http.request.env['x_township'].sudo().search([])
        state = http.request.env['x_state'].sudo().search([])
        careerfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_career')])
        programfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_program')])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        firstdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_firstdegree_attachment')])
        postdegreefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',id),('res_model','=','hr.applicant'),('x_field','=','x_postdegree_attachment')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        idata = http.request.env['x_interview'].sudo().search(['&','&',('x_applicant_id','=',aid),('x_type','=',1),('x_status','=',1)])
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=3)
        return http.request.render('website.detail-view-pe',{'state':state,'township':township,'pdata':pedata,'prodata':prodata,'invodata':invodata,'sumdata':sumdata,'verdata':verdata,'idata':idata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'academicfiles':academicfiles,'careerfiles':careerfiles,'programfiles':programfiles,'firstdegreefiles':firstdegreefiles,'postdegreefiles':postdegreefiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_view_peproexperience', type='http', auth="public", website=True)
    def detail_view_experience(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        aecdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=3)
        pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',id)])
        return http.request.render('website.detail-view-proexperience', {'pedata':pedata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paystatus':paystatus,'form_type':form_type,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm})


    @http.route('/detail_aec', type='http', auth="public", website=True)
    def detail_view_aec(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        aecdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',aecdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=3)
        return http.request.render('website.detail-view-aec', {'rtcdata':aecdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paystatus':paystatus,'form_type':form_type,'academicfiles':academicfiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_rtc', type='http', auth="public", website=True)
    def detail_view_rtc(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        rtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-rtc', {'rtcdata':rtcdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paystatus':paystatus,'form_type':form_type,'academicfiles':academicfiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_rfpe', type='http', auth="public", website=True)
    def detail_view_rfpe(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        rfpedata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        cards = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        if not cards:
           card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        if cards:
           for crd in cards:
               card = crd
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rfpedata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rfpedata.id),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #paystatus = aapay.x_payment_status
        #form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-rfpe', {'rfpedata':rfpedata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'academicfiles':academicfiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm,'mpbiafiles':mpbiafiles})

    @http.route('/detail_rgtc', type='http', auth="public", website=True)
    def detail_view_rgtc(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        rgtcdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rgtcdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        paystatus = aapay.x_payment_status
        form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-rgtc', {'pdata':rgtcdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paydata':paydata,'paystatus':paystatus,'form_type':form_type,'academicfiles':academicfiles,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_rec', type='http', auth="public", website=True)
    def detail_view_rec(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        atdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        cards = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        if not cards:
           card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        if cards:
           for crd in cards:
               card = crd
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',atdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #paystatus = aapay.x_payment_status
        #form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        apno_lid = http.request.env['hr.applicant'].sudo().search(['&',('x_approval_no','!=',''),('job_id','=',10)], order="x_approval_no desc", limit=1)
        if not apno_lid.x_approval_no:
           approval_no = apno_lid.job_id.name+'00001'
        if apno_lid.x_approval_no:
           str_no = apno_lid.x_approval_no
           str_num = str_no[-5:]
           num = int(str_num)+1
           no = '{:05d}'.format(num)
           approval_no = apno_lid.job_id.name+no
        return http.request.render('website.detail-view-rec',{'apno_lid':apno_lid,'approval_no':approval_no,'pdata':atdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paydata':paydata,'academicfiles':academicfiles,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_rlpe', type='http', auth="public", website=True)
    def detail_view_rlpe(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        atdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        cards = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        if not cards:
           card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        if cards:
           for crd in cards:
               card = crd
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',atdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',atdata.id),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #paystatus = aapay.x_payment_status
        #form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-rlpe',{'pdata':atdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paydata':paydata,'academicfiles':academicfiles,'mpbiafiles':mpbiafiles})

    @http.route('/detail_rle', type='http', auth="public", website=True)
    def detail_view_rle(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        rledata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #cards = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        #if not cards:
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rledata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',rledata.id),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #paystatus = aapay.x_payment_status
        #form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-rle', {'rledata':rledata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'academicfiles':academicfiles,'paydata':paydata,'nrc':nrc,'nrcmm':nrcmm,'mpbiafiles':mpbiafiles})

    @http.route('/detail_rsec', type='http', auth="public", website=True)
    def detail_view_rsec(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #paystatus = aapay.x_payment_status
        #form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-rsec', {'pdata':pdata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paydata':paydata,'academicfiles':academicfiles,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/detail_acpe', type='http', auth="public", website=True)
    def detail_view_acpe(self, **kw):
        id = kw.get('id')
        aid = int(id)
        par_id = request.env.user.partner_id.id
        acpedata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',acpedata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        practicefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',acpedata.id),('res_model','=','hr.applicant'),('x_field','=','x_practice')])
        paydata = http.request.env['x_payment_type'].sudo().search(['&',('x_partner','=',par_id),('x_form_type','=','Second')])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        #peid = request.website._website_form_last_record().sudo().id
        pedata = http.request.env['x_proexperience'].sudo().search([('x_applicant','=',aid)])
        #paystatus = aapay.x_payment_status
        #form_type = aapay.x_application_payment_id.x_payment_id.x_name
        if not aapay:
           paystatus = ' '
           form_type = ' '
        todaydate =  fields.Datetime.now()
        fdate = todaydate.date().strftime('%d/%m/%Y')
        edate = todaydate + relativedelta(years=1)
        return http.request.render('website.detail-view-acpe', {'pdata':acpedata,'rtcdata':pedata,'aaprecords':aapay,'todaydate':todaydate,'fdate':fdate,'edate':edate,'card':card,'paydata':paydata,'academicfiles':academicfiles,'practicefiles':practicefiles,'nrc':nrc,'nrcmm':nrcmm})

    @http.route('/cardemail', type='http', auth="public", website=True, methods=['POST'])
    def card_email(self, **post):
        id = post.get('id')
        aid = int(id)
        carddata = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        value = { 'x_remark':post.get('x_remark')}
        carddata.sudo().write(value)
        adata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        val = {'x_state':9}
        adata.sudo().write(val)
        cardid = carddata.id
        cid = str(cardid)
        test = adata.job_id.name
        useremail = adata.email_from
        adminemail = "mecportal20@gmail.com"
        datemail = fields.Datetime.now().strftime('%B %d')
        subject = "Approved list"
        subjectmail = " "
        username = adata.partner_name
        jobname = adata.job_id.name
        regno = adata.x_reg_no
        regbranch = "(09779949902)"
        jname = adata.job_id.name
        if post.get('x_remark'):
           textremark= "<span>" + post.get('x_remark')+ "</span>"
        if not post.get('x_remark'):
           textremark=" "
        textaccept = "<p><span>MEngC approved you as "+jname+" and your Approval No. – "+regno+"</span><br><span>Remark : </span>"+textremark+"<br><span>Please take payment Kyat …………………. for "+jobname+" Registration and Annual Fees by your "+jobname+" No."+regno+"</span></p>"
        message = "<table><tbody><tr><td><span>Dear "+username+"</span>"+textaccept+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
        y = send_email(useremail,message,subject)
        if y["state"]:
           url = jobname.lower()+'-registration-list'
           return http.request.redirect(url)
        if not y["state"]:
           return request.redirect('/home')

    @http.route('/paynow', type='http', auth="public", website=True)
    def pay_now(self, **kw):
        id = kw.get('id')
        apid = kw.get('apid')
        aapid = int(apid)
        aapdata = request.env['x_applicant_application_payment'].sudo().search(['&',('id','=',id),('x_applicant_id','=',aapid)])
        aapid = aapdata.x_applicant_id.partner_id.id
        pid = request.env.user.partner_id.id
        aid = aapdata.id
        apid = str(aid)
        if aapid == pid:
           return http.request.redirect('/payment?aaid='+apid)
        if not aapid == pid:
           return http.request.render('web.login',{'aaid':aapdata})

    @http.route('/issuecard', type='http', auth="public", methods=['POST'], website=True)
    def issue_card(self, **post):
        apid = post.get('x_applicant_id')
        #issue = post.get('x_issue')
        val = { 'x_issue_card' : 1}
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        value = {'x_state':10}
        pdata.sudo().write(value)
        job_id = pdata.job_id.id
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'10', 'x_applicant_id': apid, 'x_job_id':job_id }
        history.sudo().create(hvalue)
        aid = int(apid)
        carddata = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        carddata.sudo().write(val)
        url = post.get('x_link')
        jobname = pdata.job_id.name
        #return http.request.render('website.testpayment',{'aid':aid,'carddata':carddata})
        #return http.request.redirect('/'+url)
        url = jobname.lower()+'-registration-list'
        return http.request.redirect(url)

    @http.route('/my-record-test',  type='http', auth="public", website=True)
    def myrecord_list_test(self, **kw):
        tid = kw.get('id')
        id = int(tid)
        test = http.request.env['x_card'].sudo().search([('id','=',id)])
        val = request.env.user.partner_id.id
        reglists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)])
        tlists = []
        clists = []
        accdatas = []
        for reglist in reglists:
            aid = reglist.id
            tlist = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
            tlists.append(tlist)
            clist = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
            clists.append(clist)
            aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
            accdatas.append(aapays)
        return http.request.render('website.my-record-test',{'test':test,'tid':tid,'tlist':tlists,'clists':clists, 'clist':clist,'accdatas':accdatas})

    @http.route(['/review_rec'], type='http', auth='public', website=True)
    def review_rec(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.review-rec', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'ddata':ddata})

    @http.route(['/review_rlpe'], type='http', auth='public', website=True)
    def review_rlpe(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
        return http.request.render('website.review-rlpe', {'pdata':pdata,'academicfiles':academicfiles,'mpbiafiles':mpbiafiles})

    @http.route(['/review_rle'], type='http', auth='public', website=True)
    def review_rle(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
        return http.request.render('website.review-rle', {'pdata':pdata,'academicfiles':academicfiles,'mpbiafiles':mpbiafiles})

    @http.route(['/review_rsec'], type='http', auth='public', website=True)
    def review_rsec(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        ddata = http.request.env['x_discipline'].sudo().search([])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.review-rsec', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'ddata':ddata})


    @http.route(['/review_agtech'], type='http', auth='public', website=True)
    def review_agtech(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.review-agtech', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'ddata':ddata})

    @http.route(['/review_atech'], type='http', auth='public', website=True)
    def review_atech(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.review-atech', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'ddata':ddata})

    @http.route(['/review_rtc'], type='http', auth='public', website=True)
    def review_rtc(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.review-rtc', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'ddata':ddata})

    @http.route(['/review_rfpe'], type='http', auth='public', website=True)
    def review_rfpe(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        mpbiafiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_mpbia')])
        return http.request.render('website.review-rfpe', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'mpbiafiles':mpbiafiles,'ddata':ddata})

    @http.route(['/review_rgtech'], type='http', auth='public', website=True)
    def review_rgtech(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        practicefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_practice')])
        return http.request.render('website.review-rgtech', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'practicefiles':practicefiles})

    @http.route(['/review_aec'], type='http', auth='public', website=True)
    def review_aec(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pid),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        return http.request.render('website.review-aec', {'pdata':pdata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'ddata':ddata})

    @http.route(['/interview-entry'], type='http', auth='public', website=True)
    def interview_entry(self, **kw):
        id = kw.get('id')
        idata = http.request.env['x_interview'].sudo().search([('id','=',id)])
        aid = idata.x_applicant_id.id
        pdata = http.request.env['hr.applicant'].sudo().search(['&','|','|','|','|','|','|',('x_state','=',21),('x_state','=',11),('x_state','=',16),('x_state','=',18),('x_state','=',17),('x_state','=',6),('x_state','=',7),'|','|','|',('job_id','=',5),('job_id','=',10),('job_id','=',1),('job_id','=',2)])
        #pdata = http.request.env['hr.applicant'].sudo().search([('x_state','=',7)])
        lid = http.request.env['x_interview'].sudo().search([], order="id desc", limit=1)
        #type = pdata.job_id.name
        return http.request.render('website.interview-entry',{'idata':idata,'pdata':pdata,'lid':lid})

    @http.route(['/interview-list','/interview-list/page/<int:page>'], type='http', auth='public', website=True)
    def interview_list(self, page=1):
        idata = http.request.env['x_interview'].sudo().search([],offset=(page-1) * 20, limit=20, order="id desc")
        total = http.request.env['x_interview'].sudo().search_count([])
        pager = request.website.pager(
                url='/interview-list',
                total=total,
                page=page,
                step=20,
                scope=4,
        )
        return http.request.render('website.interview-list', {'idata':idata,'pager':pager})

    @http.route(['/myinterviewlist','/myinterviewlist/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def my_interviewlist(self, page=1, **post):
        #jjid = post.get('jid');
        #jid = int(jjid)
        jname = post.get('jname')
        #jstate = post.get('state')
        if jname:
           job_id = int(jname)        
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        appid = post.get('appno')
        if appid and not jname:
           apdata = http.request.env['hr.applicant'].sudo().search([('x_approval_no','=',appid)])
           if apdata.x_interview_id:
              predata = http.request.env['x_interview'].sudo().search(['&','&',('x_applicant_id','=',apdata.id),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
              total = http.request.env['x_interview'].sudo().search_count(['&','&',('x_applicant_id','=',apdata.id),('create_date','>=',start),('create_date','<=',end)])
           if not apdata.x_interview_id:
              predata = ''
        if not appid and not jname:
           predata = http.request.env['x_interview'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_interview'].sudo().search_count(['&',('create_date','>=',start),('create_date','<=',end)])
        if jname and not appid:
           predata = http.request.env['x_interview'].sudo().search(['&','&',('x_job_id','=',job_id),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_interview'].sudo().search_count(['&','&',('x_job_id','=',job_id),('create_date','>=',start),('create_date','<=',end)])
        if appid and jname:
           apdata = http.request.env['hr.applicant'].sudo().search([('x_approval_no','=',appid)])
           if apdata.x_interview_id:
              predata = http.request.env['x_interview'].sudo().search(['&','&','&',('x_applicant_id','=',apdata.id),('x_job_id','=',job_id),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
              total = http.request.env['x_interview'].sudo().search_count(['&','&','&',('x_applicant_id','=',apdata.id),('x_job_id','=',job_id),('create_date','>=',start),('create_date','<=',end)])
        pager = request.website.pager( url = '/myinterviewlist', total = total, page=page, url_args= post,step = 20, scope = 4)
        return http.request.render('website.interview-list1',{'testlist':predata,'now':now,'jname':jname,'name':name, 'start':start,'end':end,'appid':appid,'pager':pager})


       # if name:
       #    aid = int(name)
       #    name_lower = post.get('pename').lower()
       #    name_upper = post.get('pename').upper()
       # if not name:
       #    aid =' '
       #    name_lower = ' '
       #    name_upper = ' '
       # com_name = http.request.env['x_interview'].sudo().search([])
       
       # if com_name:
       #     daterange = http.request.env['x_interview'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)])
       #     res = http.request.env['x_interview'].sudo().search(['&',('x_job_id','=',state),'|','|','|','|',('x_name','like',name),('x_name','like',name_lower),('x_name','like',name_upper),('x_name','like',name),('x_applicant_id','like',aid)],offset=(page-1) * 22, limit=22)
       #     total = http.request.env['x_interview'].sudo().search_count(['|','|','|','|',('x_name','like',name),('x_name','like',name_lower),('x_name','like',name_upper),('x_name','ilike',name),('x_applicant_id','like',aid)])
       #     pager = request.website.pager(
       #          url='/interview-list1',
       #          url_args= post,
       #          total=total,
       #          page=page,
       #          step=22,
       #          scope=5,
       #     )
       #     if res:
       #         return http.request.render('website.interview-list1', {
       #         # pass company details to the webpage in a variable
       #         'testlist': res,'pager': pager,'now':now,'jname':jname,'name':name,'state':state,'start':start,'end':end,'daterange':daterange,'jstate':jstate})
       #     if not res:
       #         a = ()
       #         return http.request.render('website.interview-list1', {
       #         # pass company details to the webpage in a variable
       #         'testlist': a,'sresult':name, 'state':state,'start':start,'end':end,'jname':jname,'name':name,'jstate':jstate})


    @http.route(['/save_interview/'], type='http', auth='public', website=True, methods=['POST'])
    def save_interview(self, **post):
        id = post.get('id')
        #type = post.get('x_type')
        if not id:
           apid = post.get('x_applicant_id') 
           aid = int(apid)
           tp = post.get('x_type')
           type = str(tp)
           #apdata = http.request.env['hr.applicant'].sudo().search([('id','=',x_applicant_id)])
           indata = http.request.env['x_interview'].sudo().search(['&',('x_applicant_id','=',aid),('x_type','=',tp)])
           if indata:
              pdata = http.request.env['hr.applicant'].sudo().search(['&','|','|','|','|','|',('x_state','=',11),('x_state','=',16),('x_state','=',18),('x_state','=',17),('x_state','=',6),('x_state','=',7),'|','|',('job_id','=',10),('job_id','=',1),('job_id','=',2)])
              lid = http.request.env['x_interview'].sudo().search([], order="id desc", limit=1)
              return http.request.render('website.interview-entry',{'pdata':pdata,'lid':lid,'msg':1})
           else:
                idata = http.request.env['x_interview'].sudo().search([])
                apid = post.get('x_applicant_id')
                aid = int(apid)
                #type = post.get('x_type')
                #val = { 'x_state': 11 }
                pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
                jid = pdata.job_id.id
                tp = post.get('x_type')
                type = str(tp)
                invalue = { 'x_name': post.get('x_name'),'x_type':post.get('x_type'), 'x_applicant_id': post.get('x_applicant_id'), 'x_job_id': jid}
                idata.sudo().create(invalue)
                indata = http.request.env['x_interview'].sudo().search(['&',('x_applicant_id','=',aid),('x_type','=',tp)])
                if jid == 1 or jid == 5:
                   if tp == '1':
                      val = { 'x_state': 11 }
                      history = http.request.env['x_history'].sudo().search([])
                      hvalue = { 'x_state':'11', 'x_applicant_id': apid,'x_job_id':jid }
                      history.sudo().create(hvalue)
                   else:
                       val = {'x_state': 6}
                       history = http.request.env['x_history'].sudo().search([])
                       hvalue = { 'x_state':'6', 'x_applicant_id': apid,'x_job_id':jid }
                       history.sudo().create(hvalue)
                   #pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
                   #pdata.sudo().write(val)
                else:
                    val = { 'x_state': 11 }
                    history = http.request.env['x_history'].sudo().search([])
                    hvalue = { 'x_state':'11', 'x_applicant_id': apid,'x_job_id':jid }
                    history.sudo().create(hvalue)
                    #pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
                    #pdata.sudo().write(val)
                detail = http.request.env['x_interview_detail'].sudo().search([])
                detail.sudo().create(post)
        if id: 
           status = post.get('x_status')
           value = {
                  # 'x_applicant_id': post.get('x_applicant_id'),
                   'x_type': post.get('x_type'),
                   'x_status': post.get('x_status')
                  }
           idata = http.request.env['x_interview'].sudo().search([('id','=',id)])
           idata.sudo().write(value)
           detail = http.request.env['x_interview_detail'].sudo().search([])
           detail.sudo().create(post)
           apid = idata.x_applicant_id.id
           if status:
              if status == '1':
                 pedata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
                 jobid = pedata.job_id.id
                 if jobid == 1 or jobid == 5:
                    tp = post.get('x_type')
                    if tp == '1':
                       val = { 'x_state': 13 }
                       history = http.request.env['x_history'].sudo().search([])
                       hvalue = { 'x_state':'13', 'x_applicant_id': apid,'x_job_id':jobid }
                       history.sudo().create(hvalue)
                    else:
                        val = {'x_state': 17}
                        history = http.request.env['x_history'].sudo().search([])
                        hvalue = { 'x_state':'17', 'x_applicant_id': apid,'x_job_id':jobid }
                        history.sudo().create(hvalue)
                    type = post.get('x_type')
                    if type == '3':
                       #pe = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
                       pvalue = {'x_training_status':'17'}
                       pedata.sudo().write(pvalue)
                 else:
                     val = { 'x_state': 13 }
                     history = http.request.env['x_history'].sudo().search([])
                     hvalue = { 'x_state':'13', 'x_applicant_id': apid,'x_job_id':jobid }
                     history.sudo().create(hvalue)
                 pedata.sudo().write(val)
              if status == '2':
                 pedata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
                 jobid = pedata.job_id.id
                 if jobid == 1 or jobid == 5:
                    tp = post.get('x_type')
                    if tp == '1':
                       val = { 'x_state': 14 }
                    else:
                        val = {'x_state': 18}
                    history = http.request.env['x_history'].sudo().search([])
                    hvalue = { 'x_state':'18', 'x_applicant_id': apid,'x_job_id':jobid }
                    history.sudo().create(hvalue)
                 else:
                     val = { 'x_state': 14 }
                     history = http.request.env['x_history'].sudo().search([])
                     hvalue = { 'x_state':'14', 'x_applicant_id': apid,'x_job_id':jobid }
                     history.sudo().create(hvalue)
                 pedata.sudo().write(val)
        return http.request.redirect('/interview-list')

    @http.route('/delete_interview/', type='http', auth="public", methods=['POST'], website=True)
    def delete_interview(self, **post):
        id = post.get('id')
        idata = http.request.env['x_interview'].sudo().search([('id','=',id)])
        value = {
                  #'x_type': post.get('x_type'),
                   'x_status': 4
                 }
        idata.sudo().write(value)
        detail = http.request.env['x_interview_detail'].sudo().search([])
        detail.sudo().create(post)
        return http.request.redirect('/interview-list')


    @http.route(['/interview'], type='http', auth='public', website=True, methods=['POST'])
    def interview(self, **post):
        id = post.get('id')
        apid = int(id)
        idata = http.request.env['x_interview'].sudo().search(['&',('x_applicant_id','=',apid),('x_type','=',1)])
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        type = pdata1.job_id.name
        if idata:
           pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
           val = { 'x_state': 12 }
           pdata.sudo().write(val)
           jid = pdata.job_id.id
           history = http.request.env['x_history'].sudo().search([])
           hvalue = { 'x_state':'12', 'x_applicant_id': apid,'x_job_id':jid }
           history.sudo().create(hvalue)
           useremail = pdata1.email_from
           code = idata.x_name
           remark = post.get('x_remark')
           message = "Your interview code -"+code+" for "+type+"-"+id+". <br>Remark "+remark
           subject = "Interview"
          # return http.request.redirect('/acceptance-lists?name='+type)
           y = send_email(useremail,message,subject)
           if y["state"]:
              url = type.lower()+'_acceptance_list'
              return http.request.redirect(url)
           if not y["state"]:
              return request.redirect('/home')
        if not idata:
           ldata = http.request.env['x_interview'].sudo().search([])
           msg = 1
           pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
           type = pdata1.job_id.name
           testlist = http.request.env['hr.applicant'].sudo().search([])
           ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
           accdatas = []
           for acclist in testlist:
               accid = acclist.id
               accid1 = int(accid)
               aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
               accdatas.append(aapays)
           #return http.request.render('website.acceptance-lists', {'testlist':testlist,'msg':msg,'type':type,'accdatas':accdatas,'ilists':ilists})
           return http.request.redirect('/home')

    @http.route(['/my-payment-record','/my-payment-record/page/<int:page>'],type='http', auth="public", website=True)
    def mypaymentrecord_list(self, page=1,**kw,):
        #updata = http.request.env['hr.applicant'].sudo().search([])
        #for up in updata:
            #appdata1 = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',up.id)])
            #if appdata1:
               #value = {'x_partner_id': up.partner_id.id}
               #appdata1.sudo().write(value)
        val = request.env.user.partner_id.id
        #reglists = http.request.env['hr.applicant'].sudo().search([('partner_id.id','=',val)])        
        mypay_list = http.request.env['x_applicant_application_payment'].sudo().search([('x_partner_id','=',val)], offset=(page-1)*20, limit=20)
        total = http.request.env['x_applicant_application_payment'].sudo().search_count([('x_partner_id','=',val)])
        #tlists = []
        #clists = []
        #accdatas = []
        #total = 0
        #for reglist in reglists:
            #aid = reglist.id
            #tlist = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
            #tlists.append(tlist)
            #aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
            #count = http.request.env['x_applicant_application_payment'].sudo().search_count([('x_applicant_id','=',aid)])
           # total = http.request.env['x_applicant_application_payment'].sudo().search_count([('x_applicant_id','=',reglists.id)])
            #pager = request.website.pager(url='/my-payment-record',total=total,page=page,step=15,scope=4,)
            #if aapays:
               #accdatas.append(aapays)
               #total += count
        pager = request.website.pager( url='/my-payment-record', total=total, page=page, step=20,scope=4,  )
        return http.request.render('website.my-payment-record',{'accdatas':mypay_list, 'pager':pager})

    @http.route(['/payment-history-admin','/payment-history-admin/page/<int:page>'], type='http', auth="public", website=True)
    def payment_history_admin(self, page=1):
        accdatas = http.request.env['x_applicant_application_payment'].sudo().search([],offset=(page-1) * 15,order="write_date desc", limit=15)
        total = http.request.env['x_applicant_application_payment'].sudo().search_count([])
        pager = request.website.pager(
             url='/payment-history-admin',
             total=total,
             page=page,
             step=15,
             scope=4,
        )
        return http.request.render('website.payment-history-admin',{'accdatas':accdatas,'pager':pager})

    @http.route(['/payment-history-admin1','/payment-history-admin1/page/<int:page>'],type='http', auth="public", method=['POST'], website=True)
    def payment_history_admin1(self, page=1, **post):
        #jjid = post.get('jid');
        #jid = int(jjid)
        jname = post.get('jname')
        jstate = post.get('state')
        if jstate:
           state = int(jstate)
        if not jstate:
           state = ' '
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        #if name:
        #   aid = int(name)
        #   name_lower = post.get('pename').lower()
        #   name_upper = post.get('pename').upper()
        #if not name:
        #   aid =' '
        #   name_lower = ' '
        #   name_upper = ' '
        if name and not jstate:
           apdata = http.request.env['hr.applicant'].sudo().search(['|',('partner_name','ilike',name),('x_approval_no','=',name)])
           predata = []           
           total = 0
           if apdata:
              for ap in apdata:
                  predata1 = http.request.env['x_applicant_application_payment'].sudo().search(['&','&',('x_applicant_id','=',ap.id),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
                  count = http.request.env['x_applicant_application_payment'].sudo().search_count(['&','&',('x_applicant_id','=',ap.id),('create_date','>=',start),('create_date','<=',end)])
                  predata.append(predata1)
                  total+=count
        if not name and not jstate:
           predata = http.request.env['x_applicant_application_payment'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20,order="create_date desc")
           total = http.request.env['x_applicant_application_payment'].sudo().search_count(['&',('create_date','>=',start),('create_date','<=',end)])
        if jstate and not name:
           predata = http.request.env['x_applicant_application_payment'].sudo().search(['&','&',('x_job_id','=',state),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_applicant_application_payment'].sudo().search_count(['&','&',('x_job_id','=',state),('create_date','>=',start),('create_date','<=',end)])
        if name and jstate:
           apdata = http.request.env['hr.applicant'].sudo().search(['|',('partner_name','ilike',name),('x_approval_no','=',name)])
           predata = []
           total  = 0
           if apdata:
              for ap in apdata:
                  predata1 = http.request.env['x_applicant_application_payment'].sudo().search(['&','&','&',('x_applicant_id','=',ap.id),('x_job_id','=',state),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
                  count = http.request.env['x_applicant_application_payment'].sudo().search_count(['&','&','&',('x_applicant_id','=',ap.id),('x_job_id','=',state),('create_date','>=',start),('create_date','<=',end)])
                  predata.append(predata1)
                  total+=count
        pager = request.website.pager( url = '/payment-history-admin1', total = total, page=page, url_args= post,step = 20, scope = 4)
        return http.request.render('website.payment-history-admin1',{'total':total,'accdatas': predata,'state':state,'start':start,'end':end,'jname':jname,'name':name,'jstate':jstate,'pager':pager})
        #com_name = http.request.env['x_applicant_application_payment'].sudo().search([])
        #if com_name:
        #    daterange = http.request.env['x_applicant_application_payment'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)])
        #    res = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_job_id','=',state),'|','|','|','|',('x_name','like',name),('x_name','like',name_lower),('x_name','like',name_upper),('x_name','like',name),('x_applicant_id','like',aid)],offset=(page-1) * 22, limit=22)
        #    total = http.request.env['x_applicant_application_payment'].sudo().search_count(['|','|','|','|',('x_name','like',name),('x_name','like',name_lower),('x_name','like',name_upper),('x_name','ilike',name),('x_applicant_id','like',aid)])
        #    pager = request.website.pager(
        #         url='/payment-history-admin1',
        #         url_args= post,
        #         total=total,
        #         page=page,
        #         step=22,
        #         scope=5,
        #    )
        #    if res:
        #        return http.request.render('website.payment-history-admin1', {
        #        # pass company details to the webpage in a variable
        #        'accdatas': res,'pager': pager,'now':now,'jname':jname,'name':name,'state':state,'start':start,'end':end,'daterange':daterange,'jstate':jstate})
        #    if not res:
        #        a = ()
        #        return http.request.render('website.payment-history-admin1', {
        #        # pass company details to the webpage in a variable
        #        'accdatas': a,'sresult':name, 'state':state,'start':start,'end':end,'jname':jname,'name':name,'jstate':jstate})

    @http.route('/re-interview', type='http', auth="public", methods=['POST'], website=True)
    def re_interview(self, **post):
        apid = post.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        type = pdata.job_id.name
        jid = pdata.job_id.id
        fid1 = post.get('x_payment_id')
        fid = int(fid1)
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
        apayid1 = apay.id
        apayid = int(apayid1)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',apid),('x_application_payment_id','=',apayid)])
        if aapay:
           raise ValidationError("Need Payment.")
        if not aapay:
           Pay = http.request.env['x_applicant_application_payment']
           apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
           val = {
                   'x_applicant_id': apid,
                   'x_payment_status': 'Pending',
                   'x_application_payment_id': apayid,
                   'x_remark':post.get('x_remark'),
                   'x_job_id':pdata.job_id.id,
                   'x_partner_id':pdata.partner_id.id
                  }
           Pay.sudo().create(val)
           apid1 = int(apid)
           idata = http.request.env['x_interview'].sudo().search(['&',('x_applicant_id','=',apid1),('x_type','=',1)])
           pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',apid1)])
           type = pdata1.job_id.name
           if idata:
              pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pdata1.id)])
              val = { 'x_state': 15 }
              pdata.sudo().write(val)
              jid = pdata.job_id.id
              history = http.request.env['x_history'].sudo().search([])
              hvalue = { 'x_state':'15', 'x_applicant_id': pdata1.id, 'x_job_id':jid }
              history.sudo().create(hvalue)
              useremail = pdata1.email_from
              code = idata.x_name
              aapay1 = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',pdata1.id),('x_application_payment_id','=',apayid)])
              aaid = aapay1.id
              aaid1 = str(aaid)
              dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
              url = dynamic_url.x_name
              message = "Your payment link - "+url+aaid1
              #message = "Your re-interview code -"+code+" for "+type+"-"+apid
              subject = "Re-interview"
          # return http.request.redirect('/acceptance-lists?name='+type)
              y = send_email(useremail,message,subject)
              if y["state"]:
                 url = type.lower()+'_acceptance_list'
                 return http.request.redirect(url)
              if not y["state"]:
                 return request.redirect('/home')
           if not idata:
              ldata = http.request.env['x_interview'].sudo().search([])
              msg = 1
              pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
              type = pdata1.job_id.name
              testlist = http.request.env['hr.applicant'].sudo().search([])
              ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
              accdatas = []
              for acclist in testlist:
                  accid = acclist.id
                  accid1 = int(accid)
                  aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                  accdatas.append(aapays)
              #return http.request.render('website.acceptance-lists', {'testlist':testlist,'msg':msg,'type':type,'accdatas':accdatas,'ilists':ilists})
              return http.request.redirect('/home')

    @http.route(['/review_acpe'], type='http', auth='public', website=True)
    def review_acpe(self, **kw):
        pid = kw.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pid)])
        ddata = http.request.env['x_discipline'].sudo().search([])
        nrc = http.request.env['x_nrclist'].sudo().search([],)
        nrcmm = http.request.env['x_nrclist'].sudo().search([],)
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        practicefiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',pdata.id),('res_model','=','hr.applicant'),('x_field','=','x_practice')])
        return http.request.render('website.review-acpe', {'pdata': pdata, 'ddata': ddata,'nrc':nrc,'nrcmm':nrcmm,'academicfiles':academicfiles,'practicefiles':practicefiles})


    @http.route('/pawe-exam', type='http', auth="public", methods=['POST'], website=True)
    def pawe_exam(self, **post):
        apid = post.get('id')
        aid = int(apid)
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        type = pdata.job_id.name
        jid = pdata.job_id.id
        fid1 = post.get('x_payment_id')
        fid = int(fid1)
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
        apayid1 = apay.id
        apayid = int(apayid1)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',apid),('x_application_payment_id','=',apayid)])
        type = post.get('x_type')
        idata = http.request.env['x_interview'].sudo().search(['&',('x_applicant_id','=',aid),('x_type','=',type)])
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
        type = pdata1.job_id.name
        if idata:
           pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pdata1.id)])
           val = { 'x_state': 16 }
           pdata.sudo().write(val)
           jid = pdata.job_id.id
           history = http.request.env['x_history'].sudo().search([])
           hvalue = { 'x_state':'16', 'x_applicant_id': pdata1.id,'x_job_id':jid }
           history.sudo().create(hvalue)
           useremail = pdata1.email_from
           code = idata.x_name
           if aapay:
              raise ValidationError("Need Payment.")
           if not aapay:
              Pay = http.request.env['x_applicant_application_payment']
              apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
              val = {
                     'x_applicant_id': apid,
                     'x_payment_status': 'Pending',
                     'x_application_payment_id': apayid,
                     'x_remark':post.get('x_remark'),
                     'x_job_id':pdata.job_id.id,
                     'x_partner_id':pdata.partner_id.id
                    }
              Pay.sudo().create(val)
              apid1 = int(apid)
              aapay1 = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',pdata1.id),('x_application_payment_id','=',apayid)])
              aaid = aapay1.id
              aaid1 = str(aaid)
              rk = post.get('x_remark')
              remark = str(rk)
              dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
              url = dynamic_url.x_name
              message = "Remark - "+remark+ ". Your payment link - "+url+aaid1
              #message = "Your re-interview code -"+code+" for "+type+"-"+apid
              subject = "PAWE Exam"
          # return http.request.redirect('/acceptance-lists?name='+type)
              y = send_email(useremail,message,subject)
              if y["state"]:
                 url = type.lower()+'_acceptance_list'
                 return http.request.redirect(url)
              if not y["state"]:
                 return request.redirect('/home')
        if not idata:
           ldata = http.request.env['x_interview'].sudo().search([])
           msg = 1
           pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
           type = pdata1.job_id.name
           testlist = http.request.env['hr.applicant'].sudo().search([])
           ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
           accdatas = []
           for acclist in testlist:
               accid = acclist.id
               accid1 = int(accid)
               aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
               accdatas.append(aapays)
              #return http.request.render('website.acceptance-lists', {'testlist':testlist,'msg':msg,'type':type,'accdatas':accdatas,'ilists':ilists})
           return http.request.redirect('/home')

    @http.route('/repawe-exam', type='http', auth="public", methods=['POST'], website=True)
    def repawe_exam(self, **post):
        apid = post.get('id')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        type = pdata.job_id.name
        jid = pdata.job_id.id
        fid1 = post.get('x_payment_id')
        fid = int(fid1)
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
        apayid1 = apay.id
        apayid = int(apayid1)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',apid),('x_application_payment_id','=',apayid)])
        #if aapay:
           #raise ValidationError("Need Payment.")
        #if not aapay:
           #Pay = http.request.env['x_applicant_application_payment']
           #apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
           #val = {
                   #'x_applicant_id': apid,
                   #'x_payment_status': 'Pending',
                   #'x_application_payment_id': apayid,
                   #'x_remark':post.get('x_remark')
                  #}
           #Pay.sudo().create(val)
        apid1 = int(apid)
        type = post.get('x_type')
        idata = http.request.env['x_interview'].sudo().search(['&',('x_applicant_id','=',apid1),('x_type','=',type)])
        #idata = http.request.env['x_interview'].sudo().search([('x_applicant_id','=',apid1)])
        pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',apid1)])
        type = pdata1.job_id.name
        if idata:
           pdata = http.request.env['hr.applicant'].sudo().search([('id','=',pdata1.id)])
           val = { 'x_state': 19 }
           pdata.sudo().write(val)
           jid = pdata.job_id.id
           history = http.request.env['x_history'].sudo().search([])
           hvalue = { 'x_state':'19', 'x_applicant_id': pdata1.id,'x_job_id':jid }
           history.sudo().create(hvalue)
           useremail = pdata1.email_from
           code = idata.x_name
           if aapay:
              raise ValidationError("Need Payment.")
           if not aapay:
              Pay = http.request.env['x_applicant_application_payment']
              apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
              val = {
                     'x_applicant_id': apid,
                     'x_payment_status': 'Pending',
                     'x_application_payment_id': apayid,
                     'x_remark':post.get('x_remark'),
                     'x_job_id':pdata.job_id.id,
                     'x_partner_id':pdata.partner_id.id
                    }
              Pay.sudo().create(val)
              aapay1 = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',pdata1.id),('x_application_payment_id','=',apayid)])
              aaid = aapay1.id
              aaid1 = str(aaid)
              rk = post.get('x_remark')
              remark = str(rk)
              dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
              url = dynamic_url.x_name
              message = "Remark - "+remark+ ". Your payment link - "+url+aaid1
              #message = "Your re-interview code -"+code+" for "+type+"-"+apid
              subject = "PAWE Re-exam"
               # return http.request.redirect('/acceptance-lists?name='+type)
              y = send_email(useremail,message,subject)
              if y["state"]:
                 url = type.lower()+'_acceptance_list'
                 return http.request.redirect(url)
              if not y["state"]:
                 return request.redirect('/home')
        if not idata:
           ldata = http.request.env['x_interview'].sudo().search([])
           msg = 1
           pdata1 = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
           type = pdata1.job_id.name
           testlist = http.request.env['hr.applicant'].sudo().search([])
           ilists = http.request.env['x_interview'].sudo().search([('x_status','!=','')])
           accdatas = []
           for acclist in testlist:
               accid = acclist.id
               accid1 = int(accid)
               aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
               accdatas.append(aapays)
              #return http.request.render('website.acceptance-lists', {'testlist':testlist,'msg':msg,'type':type,'accdatas':accdatas,'ilists':ilists})
           return http.request.redirect('/home')

    @http.route(['/training-list','/training-list/page/<int:page>'], type='http', auth='public', website=True)
    def training_list(self, page=1, **kw):
        #jobtype = kw.get('jid')
        #jobid = int(jobtype)
        tdata = http.request.env['hr.applicant'].sudo().search(['&','|',('job_id','=',5),('job_id','=',1),'|','|',('x_training_status','=',18),('x_training_status','=',20),('x_training_type','=',1)],offset=(page-1) * 20, limit=20, order="id desc")
        total = http.request.env['hr.applicant'].sudo().search_count(['&',('job_id','=',1),'|',('x_training_status','=',18),('x_training_type','=',1)])
        pager = request.website.pager(
                url='/training-list',
                total=total,
                page=page,
                step=20,
                scope=4,
        )
        return http.request.render('website.training-list', {'tdata':tdata,'pager':pager})

    @http.route(['/training-entry'], type='http', auth='public', website=True)
    def training_entry(self, **kw):
        id = kw.get('id')
        tdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        lid = http.request.env['hr.applicant'].sudo().search([('x_training_status','=','18')], order="id desc", limit=1)
        return http.request.render('website.training-entry',{'tdata':tdata,'lid':lid})

    @http.route('/training-lists',  type='http', auth="public", website=True)
    def training_lists(self, **kw):
        jobid = kw.get('jid')
        jid = int(jobid)
        #tlist = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jid),'|','|','|','|',('x_state','=','17'),('x_state','=',12),('x_state','=',13),('x_state','=',14),('x_state','=',15)])
        tlist = http.request.env['hr.applicant'].sudo().search([('job_id','=',jid)])
        start = fields.Datetime.now().date()
        end =  fields.Datetime.now().date()
        accdatas = []
        for acclist in tlist:
            accid = acclist.id
            accid1 = int(accid)
            aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
            accdatas.append(aapays)
        lid = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jid),'|','|',('x_training_type','=','1'),('x_training_status','=','18'),('x_training_status','=','19')], order="id desc", limit=1)
        daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
        return http.request.render('website.training-lists',{'tlist':tlist,'accdatas':accdatas,'state':'17','lid':lid,'jid':jid,'daterange':daterange,'start':start,'end':end})

    @http.route('/training-mail', type='http', auth="public", methods=['POST'], website=True)
    def training_mail(self, **post):
        apid = post.get('id')
        remark = post.get('x_remark')
        training_code = post.get('x_training_code')
        aid = int(apid)
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        type = pdata.job_id.name
        jid = pdata.job_id.id
        fid1 = post.get('x_payment_id')
        fid = int(fid1)
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',fid),('x_application_id','=',jid)])
        apayid1 = apay.id
        apayid = int(apayid1)
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',aid),('x_application_payment_id','=',apayid)])
        if not aapay:
           todaydate =  fields.Datetime.now()
           val = { 'x_training_status': 18, 'x_training_start_date': todaydate.date(),'x_training_code': training_code }
           pdata.sudo().write(val)
           history = http.request.env['x_history'].sudo().search([])
           hvalue = { 'x_state':'20', 'x_applicant_id': aid, 'x_job_id': jid}
           history.sudo().create(hvalue)
           useremail = pdata.email_from
           #code = idata.x_name
           Pay = http.request.env['x_applicant_application_payment']
           val = {
                   'x_applicant_id': apid,
                   'x_payment_status': 'Pending',
                   'x_application_payment_id': apayid,
                   'x_remark': remark,
                   'x_job_id':pdata.job_id.id,
                   'x_partner_id':pdata.partner_id.id, 
                  }
           Pay.sudo().create(val)
           apid1 = int(apid)
           aapay1 = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',aid),('x_application_payment_id','=',apayid)])
           aaid = aapay1.id
           aaid1 = str(aaid)
           rk = str(remark)
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','payment')])
           url = dynamic_url.x_name
           message = "Remark - "+rk+ ". Your payment link - "+url+aaid1
           subject = "Training for "+type
           y = send_email(useremail,message,subject)
           jobid = str(jid)
           if y["state"]:
              return http.request.redirect('/training-lists?jid='+jobid)
           if not y["state"]:
              return request.redirect('/home')
        if aapay:
           return http.request.redirect('/home')

    @http.route('/trainingdetail', type='http', auth="public", method=['POST'], website=True, csrf=False)
    def training_detail(self, page=1, **post):
        jjid = post.get('jid')
        if jjid:
           jid = int(jjid)
        if not jjid:
           jid = ' '
        now = fields.Datetime.now().date()
        start = post.get('startdate')
        end = post.get('enddate')
        name = post.get('pename')
        state = post.get('state')
        if name:
           name_lower = post.get('pename').lower()
           name_upper = post.get('pename').upper()
        if not name:
           name_lower = ' '
           name_upper = ' '
        com_name = http.request.env['hr.applicant'].sudo().search([])
        if com_name:
            daterange = http.request.env['hr.applicant'].sudo().search(['&',('x_applied_date','>=',start),('x_applied_date','<=',end)])
            res = http.request.env['hr.applicant'].sudo().search(['&',('job_id','=',jid),'|','|','|','|','|','|','|','|','|','|',('name','like',name),('x_approval_no','like',name),('x_approval_no','ilike',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name),('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)],offset=(page-1) * 20, limit=20)
            total = http.request.env['hr.applicant'].sudo().search_count(['|','|','|','|','|','|','|','|',('name','like',name),('name','like',name_lower),('name','like',name_upper),('name','ilike',name),('id','like',name) ,('email_from','like',name),('email_from','like',name_lower),('email_from','like',name_upper),('email_from','ilike',name)])
            pager = request.website.pager(
                 url='/trainingdetail',
                 url_args= post,
                 total=total,
                 page=page,
                 step=20,
                 scope=5,
            )
            accdatas = []
            for acclist in res:
                accid = acclist.id
                accid1 = int(accid)
                aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
                if aapays:
                   accdatas.append(aapays)
                   msg = 3
                if not aapays:
                   msg = 4
            if res:
                return http.request.render('website.training-lists', {
                # pass company details to the webpage in a variable
                'tlist': res,'pager': pager,'now':now,'name':name ,'jid':jid ,'state':state,'accdatas':accdatas,'start':start,'end':end,'daterange':daterange})
            if not res:
                a = ()
                return http.request.render('website.training-lists', {
                # pass company details to the webpage in a variable
                'tlist': a,'sresult':name, 'jid':jid,'start': start,'end':end,'state':state,'name':name})

    @http.route('/trainingtype', type='http', auth="public", methods=['POST'], website=True)
    def training_type(self, **post):
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        training_status = post.get('x_training_status')
        if training_status == '18':
           msg = 'This user is not enrolled'
           tdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
           lid = http.request.env['hr.applicant'].sudo().search([('x_training_status','=','18')], order="id desc", limit=1)
           return http.request.render('website.training-entry',{'tdata':tdata,'lid':lid,'msg':msg})
        else:
            val = { 'x_training_type' : 1,'x_training_status':19, 'x_training_complete_date':todaydate.date()}
            pdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
            pdata.sudo().write(val)
        return http.request.redirect('/training-list')

    @http.route('/enroll', type='http', auth="public", website=True, methods=['POST'])
    def enroll(self, **post):
        id = post.get('aid')
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        jid = pdata.job_id.id
        val = {'x_training_status':'20'}
        pdata.sudo().write(val)
        useremail = pdata.email_from
        username = pdata.partner_name
        name = str(username).replace(' ','-')
        udata = http.request.env['res.users'].sudo().search([('login','=',useremail)])
        password = udata.x_password
        datas = {
                 "email":useremail,
                 "password":password,
                 "name":name, 
                 "username":name,
                 "country":"myanmar",
                 "honor_code":"true",
                 "terms_of_service":"true",
                }
        emailheaders = {'content-type': 'application/x-www-form-urlencoded'}
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','enroll')])
        url = dynamic_url.x_name
        #url = "http://52.230.32.167/user_api/v1/account/registration/"
        response = requests.post(url, data=datas, headers=emailheaders)
        y = response.json()
        tlist = http.request.env['hr.applicant'].sudo().search(['&',('x_training_status','=','17'),('job_id','=',jid)])
        aid = str(id)
        job_type = pdata.job_id.name
        adminemail = "mecportal20@gmail.com"
        datemail = fields.Datetime.now().strftime('%B %d')
        #datemail = str(datemail1)
        subject = "Enrollment"
        subjectmail = " "
        jobname = pdata.job_id.name
        regbranch = "(01-2316995 / 01-2316891)"
        textenroll = "<p><span>Dear "+username+"</span><br><span>You can attend Training the following link and username  and password are similary with Myanmar Engineering Council Account and your training link - http.example.com</span></p>"
        message = "<table><tbody><tr><td><span>"+textenroll+"<p><span>Best Regards</span><br><span>Registration Branch "+regbranch+"</span><br><span>Myanmar Engineering Council (MEngC)</span></p></td></tr></tbody></table>"
        e = send_email(useremail,message,subject)
              #if y["state"]:
        accdatas = []
        for acclist in tlist:
            accid = acclist.id
            accid1 = int(accid)
            aapays = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',accid1)])
            accdatas.append(aapays)

        res_success = ' '
        msg = ' '
        res_email = ' '
        email_message = ' '
        res_username = ' '
        username_message = ' '
        if "success" in y:
            res_success = y["success"]
            msg = 'Successfully enrolled.'
        else:
            msg = 'This user is already enrolled.'
            res_success = ' '
            if "email" in y:
                res_email = y["email"]
                for res in res_email:
                    email_message = res['user_message']
            if "username" in y:
                res_username = y["username"]
                for resp in res_username:
                    username_message = resp['user_message']
        #return http.request.render('website.testpayment',{'udata':udata,'password':password,'result':y,'email':useremail,'name':name,'res_success':res_success,'res_email':res_email,'email_message':email_message,'res_username':res_username,'username_message':username_message,'msg':msg})
        return http.request.render('website.training-lists',{'tlist':tlist,'accdatas':accdatas,'state':'17','jid':jid,'res_success':res_success,'res_email':res_email,'email_message':email_message,'res_username':res_username,'username_message':username_message,'msg':msg})

    @http.route('/report', type='http', auth="public", website=True, methods=['POST'])
    def report(self, **post):
        apid = post.get('id')
        id = int(apid)
        pdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        #val = { 'x_training_status':'20'}
        val = { 'x_state': 21}
        pdata.sudo().write(val)
        type = pdata.job_id.name
        url = type.lower()+'_acceptance_list'
        return http.request.redirect(url)


    @http.route(['/certificatelist','/certificatelist/page/<int:page>'], type='http', auth='public', website=True)
    def certificate_list(self, page=1,**post):
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','certificateList')])
        #url = "http://13.76.253.98:8080/api/cretificateList"
        url = dynamic_url.x_name
        response = requests.get(url)
        res = response.json()
        result = res.values()
        #res_array = []
        for res_value in result:
            resarray = res_value
        #obj = ast.literal_eval(datastring)
        res_array = ast.literal_eval(resarray)
        Cert_data = http.request.env['x_certificate'].sudo().search([]).unlink()
        for re in res_array:
            val = {
                    'x_name': re['card_id'],
                    'x_application_type': re['application_type'],
                    'x_applicant_id': re['applicant_id'],
                    'x_member_date': re['member_date'],
                    'x_end_date': re['end_date'],
                    'x_remark': re['remark']
                  }
            Certificate = http.request.env['x_certificate'].sudo().create(val)
        #cedata = http.request.env['x_certificate'].sudo().search([])
        cedata = http.request.env['x_certificate'].sudo().search([],offset=(page-1) * 20, limit=20)
        total = http.request.env['x_certificate'].sudo().search_count([])
        pager = request.website.pager(
               url='/certificatelist',
               total=total,
               page=page,
               url_args= post,
               step=20,
               scope=4,
          )
        return http.request.render('website.certificatelist',{'res':res,'result':result,'res_array':res_array,'response':response,'cedata':cedata,'pager':pager})

    @http.route(['/prerequistic-list','/prerequistic-list/page/<int:page>'], type='http', auth='public', website=True)
    def prerequistic_list(self, page=1):
        #start = fields.Datetime.now().date()
        start = '2020-12-01'
        end = fields.Datetime.now().date()
        predata = http.request.env['x_prerequistic'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)], offset=(page-1)*20, limit=20)
        total = http.request.env['x_prerequistic'].sudo().search_count(['&',('create_date','>=',start),('create_date','<=',end)])
        pager = request.website.pager( url = '/prerequistic-list', total = total, page=page, step = 20, scope = 4)
        jobdata = http.request.env['hr.job'].sudo().search([])
        daterange = http.request.env['x_prerequistic'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)])
        position = 'all'
        return http.request.render('website.prerequistic-list', {'predata':predata,'jobdata':jobdata,'predata':predata,'start':start,'end':end,'daterange':daterange,'pager':pager,'position':position})

    @http.route('/prerequistic-entry', type='http', auth='public', website=True)
    def prerequistic_entry(self, **kw):
        id = kw.get('id')
        predata = http.request.env['x_prerequistic'].sudo().search([('id','=',id)])
        jobdata = http.request.env['hr.job'].sudo().search([])
        lid = http.request.env['x_prerequistic'].sudo().search([], order="id desc", limit=1)
        return http.request.render('website.prerequistic-entry',{'lid':lid,'jobdata':jobdata,'predata':predata})

    @http.route(['/save_prerequistic/'], type='http', auth='public', website=True, methods=['POST'])
    def save_prerequistic(self, **post):
        id = post.get('id')
        predata = http.request.env['x_prerequistic']
        val = { 
               'x_description': post.get('x_description'),
               'x_pre_type': post.get('x_pre_type'),
               'x_name': post.get('x_name'),
               'x_serial_number': post.get('x_serial_number')
              }
        if not id:
           serialnum = post.get('x_serial_number')
           type = post.get('x_pre_type')
           jobid = int(type)
           prdata = http.request.env['x_prerequistic'].sudo().search([('x_pre_type','=',jobid),('x_serial_number','=',serialnum)])
           if not prdata:
              predata.sudo().create(val)
           if prdata:
              #predata = http.request.env['x_prerequistic'].sudo().search([('id','=',id)])
              jobdata = http.request.env['hr.job'].sudo().search([])
              lid = http.request.env['x_prerequistic'].sudo().search([], order="id desc", limit=1)
              description =  post.get('x_description')
              pre_type =  post.get('x_pre_type')
              name = post.get('x_name')
              serial_number = post.get('x_serial_number')
              return http.request.render('website.prerequistic-entry',{'lid':lid,'jobdata':jobdata,'description':description,'pre_type':pre_type,'name':name,'serial_number':serial_number,'msg':'Wrong'})
        if id:
           predata = http.request.env['x_prerequistic'].sudo().search([('id','=',id)])
           predata.sudo().write(val)
        return http.request.redirect('/prerequistic-list') 


    @http.route(['/prerequistic_list_detail','/prerequistic_list_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def prerequistic_detail(self, page=1,**post):
        code = post.get('code')
        start = post.get('startdate')
        #start = '12/01/2020'
        end = post.get('enddate')
        pre_type = post.get('x_pre_type')
        if not pre_type:
           position = 'all'
        if pre_type:
           type = int(pre_type)
           position = 'select'
        #jobdata = http.request.env['hr.job'].sudo().search([])
        jobdata = http.request.env['hr.job'].sudo().search([])
        #daterange = http.request.env['x_prerequistic'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)])
        if code and not pre_type:
           predata = http.request.env['x_prerequistic'].sudo().search(['&','&',('x_name','ilike',code),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_prerequistic'].sudo().search_count(['&','&',('x_name','ilike',code),('create_date','>=',start),('create_date','<=',end)])
        if not code and not pre_type:
           predata = http.request.env['x_prerequistic'].sudo().search(['&',('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_prerequistic'].sudo().search_count(['&',('create_date','>=',start),('create_date','<=',end)])
        if pre_type and not code:
           predata = http.request.env['x_prerequistic'].sudo().search(['&','&',('x_pre_type','=',type),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_prerequistic'].sudo().search_count(['&','&',('x_pre_type','=',type),('create_date','>=',start),('create_date','<=',end)])
        if code and pre_type:
           predata = http.request.env['x_prerequistic'].sudo().search(['&','&','&',('x_name','ilike',code),('x_pre_type','=',type),('create_date','>=',start),('create_date','<=',end)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_prerequistic'].sudo().search_count(['&','&','&',('x_name','ilike',code),('x_pre_type','=',type),('create_date','>=',start),('create_date','<=',end)])
        pager = request.website.pager( url = '/prerequistic_list_detail', total = total, page=page,url_args= post, step = 20, scope = 4)
        return http.request.render('website.prerequistic-list',{'predata':predata,'jobdata':jobdata,'start':start,'end':end,'type':pre_type,'pager':pager,'position':position,'code':code})

    @http.route(['/renewal_list','/renewal_list/page/<int:page>'], type='http', auth='public', website=True)
    def renewal_list(self, page=1):
        renewal_data = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','10'),'|','|',('job_id','=',1),('job_id','=',5),('job_id','=',10)], offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','10'),'|','|',('job_id','=',1),('job_id','=',5),('job_id','=',10)])
        pager = request.website.pager( url = '/renewal_list', total = total, page=page, step = 20, scope = 4)
        position = 'all'
        return http.request.render('website.renewal-list', {'renewal_data':renewal_data,'position':position,'pager':pager})


    @http.route(['/renewal_rec_detail','/renewal_rec_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_rec_detail(self, page=1,**post):
        search_val = post.get('x_search')
        jid = post.get('jid')
        jname = post.get('jname')
        state = post.get('state')
        jobid = int(jid)
        start = post.get('startdate')
        end = post.get('enddate')
        renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        pager = request.website.pager( url = '/renewal_rec_detail', total = total, page=page, url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-rec-detail',{'testlist':renewal_data,'pager':pager, 'start':start,'end':end,'search_val':search_val,'jid':jobid,'jname': jname,'state':state})

    @http.route(['/renewal_rle_detail','/renewal_rle_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_rle_detail(self, page=1,**post):
        search_val = post.get('x_search')
        jid = post.get('jid')
        jname = post.get('jname')
        state = post.get('state')
        jobid = int(jid)
        start = post.get('startdate')
        end = post.get('enddate')
        renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        pager = request.website.pager( url = '/renewal_rle_detail', total = total, page=page, url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-rle-detail',{'testlist':renewal_data,'pager':pager, 'start':start,'end':end,'search_val':search_val,'jid':jobid,'jname': jname,'state':state})



    @http.route(['/renewal_rsec_detail','/renewal_rsec_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_rsec_detail(self, page=1,**post):
        search_val = post.get('x_search')
        jid = post.get('jid')
        jname = post.get('jname')
        state = post.get('state')
        cpd_Status = post.get('cpdStatus')
        jobid = int(jid)
        start = post.get('startdate')
        end = post.get('enddate')
        if cpd_Status:
           cpdStatus = int(cpd_Status)
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        if not cpd_Status:
           cpdStatus = 1
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        pager = request.website.pager( url = '/renewal_rsec_detail', total = total, page=page, url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-rsec-detail',{'testlist':renewal_data,'pager':pager, 'search_val':search_val,'jid':jobid,'start':start,'end':end,'jname': jname,'state':state,'cpdStatus': cpdStatus})

    @http.route(['/renewal_rfpe_detail','/renewal_rfpe_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_rfpe_detail(self, page=1,**post):
        search_val = post.get('x_search')
        jid = post.get('jid')
        jname = post.get('jname')
        state = post.get('state')
        cpd_Status = post.get('cpdStatus')
        jobid = int(jid)
        start = post.get('startdate')
        end = post.get('enddate')
        if cpd_Status:
           cpdStatus = int(cpd_Status)
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
        if not cpd_Status:
           cpdStatus = 1
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        pager = request.website.pager( url = '/renewal_rfpe_detail', total = total, page=page, url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-rfpe-detail',{'testlist':renewal_data,'pager':pager, 'search_val':search_val,'jid':jobid,'start':start,'end':end,'jname': jname,'state':state,'cpdStatus': cpdStatus})

    @http.route(['/renewal_rlpe_detail','/renewal_rlpe_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_rlpe_detail(self, page=1,**post):
        search_val = post.get('x_search')
        jid = post.get('jid')
        jname = post.get('jname')
        state = post.get('state')
        cpd_Status = post.get('cpdStatus')
        jobid = int(jid)
        start = post.get('startdate')
        end = post.get('enddate')
        if cpd_Status:
           cpdStatus = int(cpd_Status)
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
        if not cpd_Status:
           cpdStatus = 1
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        pager = request.website.pager( url = '/renewal_rlpe_detail', total = total, page=page, url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-rlpe-detail',{'testlist':renewal_data,'pager':pager, 'search_val':search_val,'jid':jobid,'start':start,'end':end,'jname': jname,'state':state,'cpdStatus': cpdStatus})

    @http.route(['/renewal_detail','/renewal_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_detail(self, page=1,**post):
        search_val = post.get('x_search')
        jid = post.get('jid')
        jname = post.get('jname')
        state = post.get('state')
        cpd_Status = post.get('cpdStatus')
        jobid = int(jid)
        start = post.get('startdate')
        end = post.get('enddate')
        if cpd_Status:
           cpdStatus = int(cpd_Status)
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('x_cpd_status','=',cpdStatus),('job_id','=',jobid),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        if not cpd_Status:
           cpdStatus = 1
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&','&',('x_renewal_date','>=',start),('x_renewal_date','<=',end),('job_id','=',jobid),('x_state','=',state),'|','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('partner_name','ilike',search_val),('email_from','ilike',search_val)])
        pager = request.website.pager( url = '/renewal_detail', total = total, page=page, url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-detail-list',{'testlist':renewal_data,'pager':pager, 'start':start,'end':end,'search_val':search_val,'jid':jobid, 'jname': jname,'state':state,'cpdStatus': cpdStatus})


    @http.route(['/renewal_list_detail','/renewal_list_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def renewal_list_detail(self, page=1,**post):
        job_type = post.get('x_type')
        if job_type:
           type = int(job_type)
        if not job_type:
           type = 0
        search_val = post.get('x_search')
        x_search = search_val.strip()
        #if not post.get('x_search'):
           #x_search = ' '
        if not type:
           position = 'all'
        if type:
           position = 'select'
        if job_type and not post.get('x_search'):
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=','10'),('job_id','=',type)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=','10'),('job_id','=',type)])
        if not job_type:
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&',('x_state','=','10'),'|',('name','ilike',x_search),('id','like',x_search),'|','|',('job_id','=',1),('job_id','=',5),('job_id','=',10)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&',('x_state','=','10'),'|',('name','ilike',x_search),('id','like',x_search),'|','|',('job_id','=',1),('job_id','=',5),('job_id','=',10)])
        if job_type and post.get('x_search'):
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&','&',('x_state','=','10'),('job_id','=',type),'|',('partner_name','ilike',x_search),('id','like',x_search)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&','&',('x_state','=','10'),('job_id','=',type),'|',('partner_name','ilike',x_search),('id','like',x_search)])
        pager = request.website.pager( url = '/renewal_list_detail', total = total, page=page,url_args= post, step = 20, scope = 4)
        return http.request.render('website.renewal-list', {'renewal_data':renewal_data,'position':position,'pager':pager,'type':type,'x_search' : x_search})

    @http.route(['/update_cpd/'], type='http', auth='public', website=True, methods=['POST'])
    def update_cpd(self, **post):
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        apdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        if post.get('x_re_id'):
           FileStorage = post.get('x_re_id')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_re_id = base64.encodestring(FileData)
        if not post.get('x_re_id'):
           x_re_id = apdata.x_re_id
        if post.get('x_re_id_name'):
           x_re_id_name = post.get('x_re_id_name')
        if not post.get('x_re_id_name'):
           x_re_id_name = apdata.x_re_id_name
        value = {'x_cpd_status': 1, 'x_re_id': x_re_id, 'x_re_id_name': x_re_id_name}
        apdata.sudo().write(value)
        return http.request.redirect('/my-record')



    @http.route(['/update_renewal/'], type='http', auth='public', website=True, methods=['POST'])
    def update_renewal(self, **post):
        id = post.get('id')
        todaydate =  fields.Datetime.now()
        apdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        academicfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',apdata.id),('res_model','=','hr.applicant'),('x_field','=','x_academic')])
        identityfiles = http.request.env['ir.attachment'].sudo().search(['&',('res_id','=',apdata.id),('res_model','=','hr.applicant'),('x_field','=','x_identity_card')])
        if request.httprequest.method == 'POST':
           if 'x_academic' in request.params:
              attached_files = request.httprequest.files.getlist('x_academic')
              import base64
              if attached_files:
                 academicfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  academicfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': apdata.id,
                        'type': 'binary',
                        'x_field': 'x_academic',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if request.httprequest.method == 'POST':
           if 'x_identity_card' in request.params:
              attached_files = request.httprequest.files.getlist('x_identity_card')
              import base64
              if attached_files:
                 identityfiles.sudo().unlink()
              for attachment in attached_files:
                  FileExtension = attachment.filename.split('.')[-1].lower()
                  ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','jpeg','pdf','zip','rar']
                  if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
                     return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
                  attached_file = attachment.read()
                  org_filename = attachment.filename
                  filename_without_extension = os.path.splitext(org_filename)[0]
                  #todaydate =  fields.Datetime.now()
                  datetime_String = fields.Datetime.now().strftime('%Y-%m-%d-%H:%M')
                  random_number = str(randint(10000, 99999))
                  file_extension = pathlib.Path(org_filename).suffix
                  final_filename = filename_without_extension + datetime_String+ random_number+file_extension
                  identityfiles.sudo().create({
                        'name': final_filename,
                        'res_model': 'hr.applicant',
                        'res_id': apdata.id,
                        'type': 'binary',
                        'x_field': 'x_identity_card',
                        'public':'true',
                        'datas': base64.encodestring(attached_file),
                    })
        if post.get('x_nrc_photo_front'):
           FileStorage = post.get('x_nrc_photo_front')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_front = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_front'):
           x_nrc_photo_front = apdata.x_nrc_photo_front
        if post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = post.get('x_nrc_photo_front_name')
        if not post.get('x_nrc_photo_front_name'):
           x_nrc_photo_front_name = apdata.x_nrc_photo_front_name
        if post.get('x_nrc_photo_back'):
           FileStorage = post.get('x_nrc_photo_back')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_nrc_photo_back = base64.encodestring(FileData)
        if not post.get('x_nrc_photo_back'):
           x_nrc_photo_back = apdata.x_nrc_photo_back
        if post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = post.get('x_nrc_photo_back_name')
        if not post.get('x_nrc_photo_back_name'):
           x_nrc_photo_back_name = apdata.x_nrc_photo_back_name
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
              return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        if not post.get('x_photo'):
           x_photo = apdata.x_photo
        if post.get('x_re_id'):
           FileStorage = post.get('x_re_id')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib','heif','heic','ind','indd','indt','jp2','j2k','jpf','jpx','jpm','mj2','svg','svgz','ai','eps']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_re_id = base64.encodestring(FileData)
        if not post.get('x_re_id'):
           x_re_id = apdata.x_re_id
        if post.get('x_re_id_name'):
           x_re_id_name = post.get('x_re_id_name')
        if not post.get('x_re_id_name'):
           x_re_id_name = apdata.x_re_id_name
        if post.get('x_passportattachment'):
           FileStorage = post.get('x_passportattachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_passportattachment = base64.encodestring(FileData)
        if not post.get('x_passportattachment'):
           x_passportattachment = apdata.x_passportattachment
        if post.get('x_passportattachment_filename'):
           x_passportattachment_filename = post.get('x_passportattachment_filename')
        if not post.get('x_passportattachment_filename'):
           x_passportattachment_filename = apdata.x_passportattachment_filename
        if post.get('x_rec_attachment'):
           FileStorage = post.get('x_rec_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rec_attachment = base64.encodestring(FileData)
        if not post.get('x_rec_attachment'):
           x_rec_attachment = apdata.x_rec_attachment
        if post.get('x_rec_attachment_filename'):
           x_rec_attachment_filename = post.get('x_rec_attachment_filename')
        if not post.get('x_rec_attachment_filename'):
           x_rec_attachment_filename = apdata.x_rec_attachment_filename
        if post.get('x_rsec_attachment'):
           FileStorage = post.get('x_rsec_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rsec_attachment = base64.encodestring(FileData)
        if not post.get('x_rsec_attachment'):
           x_rsec_attachment = apdata.x_rsec_attachment
        if post.get('x_rsec_attachment_filename'):
           x_rsec_attachment_filename = post.get('x_rsec_attachment_filename')
        if not post.get('x_rsec_attachment_filename'):
           x_rsec_attachment_filename = apdata.x_rsec_attachment_filename
        if post.get('x_rle_attachment'):
           FileStorage = post.get('x_rle_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rle_attachment = base64.encodestring(FileData)
        if not post.get('x_rle_attachment'):
           x_rle_attachment = apdata.x_rle_attachment
        if post.get('x_rle_attachment_filename'):
           x_rle_attachment_filename = post.get('x_rle_attachment_filename')
        if not post.get('x_rle_attachment_filename'):
           x_rle_attachment_filename = apdata.x_rle_attachment_filename
        if post.get('x_rfpe_attachment'):
           FileStorage = post.get('x_rfpe_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rfpe_attachment = base64.encodestring(FileData)
        if not post.get('x_rfpe_attachment'):
           x_rfpe_attachment = apdata.x_rfpe_attachment
        if post.get('x_rfpe_attachment_filename'):
           x_rfpe_attachment_filename = post.get('x_rfpe_attachment_filename')
        if not post.get('x_rfpe_attachment_filename'):
           x_rfpe_attachment_filename = apdata.x_rfpe_attachment_filename
        if post.get('x_rlpe_ttachment'):
           FileStorage = post.get('x_rlpe_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_rfpe_attachment = base64.encodestring(FileData)
        if not post.get('x_rlpe_attachment'):
           x_rlpe_attachment = apdata.x_rlpe_attachment
        if post.get('x_rlpe_attachment_filename'):
           x_rlpe_attachment_filename = post.get('x_rlpe_attachment_filename')
        if not post.get('x_rlpe_attachment_filename'):
           x_rlpe_attachment_filename = apdata.x_rlpe_attachment_filename
        if post.get('x_pe_attachment'):
           FileStorage = post.get('x_pe_attachment')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
               return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_pe_attachment = base64.encodestring(FileData)
        if not post.get('x_pe_attachment'):
           x_pe_attachment = apdata.x_pe_attachment
        if post.get('x_pe_attachment_filename'):
           x_pe_attachment_filename = post.get('x_pe_attachment_filename')
        if not post.get('x_pe_attachment_filename'):
           x_pe_attachment_filename = apdata.x_pe_attachment_filename
        values = {
                     'partner_name':post.get('partner_name'),
                     #'x_reg_no':post.get('x_reg_no'),
                     'x_nrc1en':post.get('x_nrc1en'),
                     'x_nrc2en':post.get('x_nrc2en'),
                     'x_nrc3en':post.get('x_nrc3en'),
                     'x_nrc4en':post.get('x_nrc4en'),
                     'x_nrc_no_en':post.get('x_nrc_no_en'),
                     'x_dob':post.get('x_dob'),
                     'x_pe_registration_valid_date':post.get('x_pe_registration_valid_date'),
                     'x_rec_registration_valid_date':post.get('x_rec_registration_valid_date'),
                     'x_rsec_registration_valid_date':post.get('x_rsec_registration_valid_date'),
                     'x_rle_registration_valid_date':post.get('x_rle_registration_valid_date'),
                     'x_rfpe_registration_valid_date':post.get('x_rfpe_registration_valid_date'),
                     'x_rlpe_registration_valid_date':post.get('x_rlpe_registration_valid_date'),
                     'x_engineering_discipline':post.get('x_engineering_discipline'),
                     'x_firstdegree_engineer_discipline':post.get('x_firstdegree_engineer_discipline'),
                     'x_firstdegree_graduation_year':post.get('x_firstdegree_graduation_year'),
                     'x_address_en':post.get('x_address_en'),
                     'partner_phone':post.get('partner_phone'),
                     'email_from':post.get('email_from'),
                     'x_nrc_photo_front':x_nrc_photo_front,
                     'x_nrc_photo_front_name':x_nrc_photo_front_name,
                     'x_nrc_photo_back':x_nrc_photo_back,
                     'x_nrc_photo_back_name':x_nrc_photo_back_name,
                     'x_re_id':x_re_id,
                     'x_re_id_name': x_re_id_name,
                     'x_photo':x_photo,
                     'x_state':'22',
                     'x_renewal_date': todaydate,
                     'x_passportno': post.get('x_passportno'),
                     'x_passportattachment': x_passportattachment,
                     'x_passportattachment_filename': x_passportattachment_filename,
                     'x_pe_attachment': x_pe_attachment,
                     'x_pe_attachment_filename': x_pe_attachment_filename,
                     'x_rec_attachment': x_rec_attachment,
                     'x_rec_attachment_filename': x_rec_attachment_filename,
                     'x_rsec_attachment': x_rsec_attachment,
                     'x_rsec_attachment_filename': x_rsec_attachment_filename,
                     'x_rle_attachment': x_rle_attachment,
                     'x_rle_attachment_filename': x_rle_attachment_filename,
                     'x_rlpe_attachment': x_rlpe_attachment,
                     'x_rlpe_attachment_filename': x_rlpe_attachment_filename,
                     'x_rfpe_attachment': x_rfpe_attachment,
                     'x_rfpe_attachment_filename': x_rfpe_attachment_filename,
                    }
        apdata.sudo().write(values)
        history = http.request.env['x_history'].sudo().search([])
        hvalue = { 'x_state':'22', 'x_applicant_id': apdata.id, 'x_job_id': apdata.job_id.id }
        history.sudo().create(hvalue)
        return http.request.redirect('/my-record')
        
    @http.route(['/reverse_renewal/'], type='http', auth='public', website=True, methods=['POST'])
    def reverse_renewal(self, **post):
        apid = post.get('aid')
        a_id = int(apid)
        phone = post.get('x_phone')
        address = post.get('x_address')
        mdate = post.get('x_start_date')
        edate = post.get('x_expire_date')
        price = post.get('x_price')
        card_history = http.request.env['x_card_history'].sudo().search([('x_applicant_id','=',a_id)],order="id desc", limit=1)    
        renewal_history = http.request.env['x_renewal_history'].sudo().search([('x_applicant_id','=',a_id)],order="id desc", limit=1)
        if card_history and renewal_history:
           ap_value = { 'x_is_active': False, 'x_photo': renewal_history.x_photo, 'partner_phone': renewal_history.x_partner_phone, 'x_address_en': renewal_history.x_address_en }
           c_value = { 'x_start_date': card_history.x_start_date, 'x_expire_date': card_history.x_expire_date }
           apdata = http.request.env['hr.applicant'].sudo().search([('id','=',a_id)])
           apdata.sudo().write(ap_value)
           cdata = http.request.env['x_card'].sudo().search([('x_applicant_id','=',a_id)])
           cdata.write(c_value)
           renewal_date = { 'x_renewal_date': post.get('x_reverse_date')}
           card_price = { 'x_price': cdata.x_price }
           card_history.write(card_price)
           #card_history.write(active_toggle)
           renewal_history.write(renewal_date)
        #return http.request.render('website.testpayment',{ 'card_history': card_history, 'renewal_history': renewal_history, 'apdata':apdata,'cdata':cdata})
           return http.request.redirect('/renewal_list')
        #if not card_history or not renewal_history:
           #msg = 'This record can not reverse'
           #return http.request.redirect('/home')

    @http.route(['/my_renewal_detail','/my_renewal_detail/page/<int:page>'], type='http', auth='public', methods=['POST'],website=True)
    def my_renewal_detail(self,page=1,**post):
        jid = post.get('jid')
        jobid = int(jid)
        search_val = post.get('x_search')
        userid = request.env.user.partner_id.id
        renewal_data = http.request.env['x_renewal'].sudo().search(['&','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('x_application_type','=',jobid),('x_user_id','=',userid)],offset=(page-1)*20, limit=20)
        total = http.request.env['x_renewal'].sudo().search_count(['&','|','|',('x_reg_no','ilike',search_val),('x_approval_no','ilike',search_val),('x_user_id','=',userid),('x_application_type','=',jobid)])
        pager = request.website.pager( url = '/my_renewal_detail', total = total, page=page, url_args= post,step = 20, scope = 4)
        return http.request.render('website.my-renewal-history', {'renewal_data':renewal_data,'pager':pager,'jid':jid,'search_val':search_val})


    @http.route(['/my_renewal_history','/my_renewal_history/page/<int:page>'], type='http', auth='public', website=True)
    def my_renewal_history(self, page=1):
        userid = request.env.user.partner_id.id
        renewal_data = http.request.env['x_renewal'].sudo().search([('x_user_id','=',userid)],offset=(page-1)*20, limit=20)
        total = http.request.env['x_renewal'].sudo().search_count([('x_user_id','=',userid)])
        pager = request.website.pager( url = '/my_renewal_history', total = total, page=page, step = 20, scope = 4)
        return http.request.render('website.my-renewal-history', {'renewal_data':renewal_data,'pager':pager})


    @http.route(['/my_renewal_list','/my_renewal_list/page/<int:page>'], type='http', auth='public', website=True)
    def my_renewal_list(self, page=1):
        userid = request.env.user.partner_id.id
        renewal_data = http.request.env['hr.applicant'].sudo().search(['&',('partner_id','=',userid),'&','|',('x_state','=','22'),('x_state','=','10'),'|','|',('job_id','=',1),('job_id','=',5),('job_id','=',10)], offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count(['&',('partner_id','=',userid),'&','|',('x_state','=','22'),('x_state','=','10'),'|','|',('job_id','=',1),('job_id','=',5),('job_id','=',10)])
        pager = request.website.pager( url = '/my_renewal_list', total = total, page=page, step = 20, scope = 4)
        position = 'all'
        return http.request.render('website.my-renewal-list', {'renewal_data':renewal_data,'position':position,'pager':pager})

    @http.route(['/edit_renewal/'], type='http', auth='public', website=True, methods=['POST'])
    def edit_renewal(self, **post):
        apid = post.get('id')
        phone = post.get('partner_phone')
        address = post.get('x_address_en')
        address_mm = post.get('x_address_mm')
        mdate = post.get('x_start_date')
        edate = post.get('x_expire_date')
        price = post.get('x_price')
        todaydate =  fields.Datetime.now()
        if post.get('x_photo'):
           FileStorage = post.get('x_photo')
           FileExtension = FileStorage.filename.split('.')[-1].lower()
           ALLOWED_IMAGE_EXTENSIONS = ['jpg','png','gif','pdf','jpeg','jpe','jif','jfif','jfi','webp','tiff','tif','psd','raw','arw','cr2','nrw','k25','bmp','dib']
           if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
              return json.dumps({'status':400, 'message':_("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
           import base64
           FileData = FileStorage.read()
           x_photo = base64.encodestring(FileData)
        apdata = http.request.env['hr.applicant'].sudo().search([('id','=',apid)])
        #cdata = http.request.env['x_card'].sudo().search([('x_applicant_id','=',apdata.id)])
        if not post.get('x_photo'):
           x_photo = apdata.x_photo
        re_history = { 'x_is_active': True, 'x_photo': apdata.x_photo, 'x_renewal_date': todaydate,  'x_partner_phone': apdata.partner_phone, 'x_address_en': apdata.x_address_en ,'x_address_mm': apdata.x_address_mm,'x_applicant_id': apdata.id, 'x_job_id': apdata.job_id.id, 'x_nrc_no_en':apdata.x_nrc_no_en, 'x_nrc_no_mm': apdata.x_nrc_no_mm, 'x_state': apdata.x_state}
        #c_history = {'x_is_active': False, 'x_start_date': cdata.x_start_date, 'x_expire_date': cdata.x_expire_date, 'x_applicant_id': cdata.x_applicant_id.id }
        #prev_card = http.request.env['x_card_history'].sudo().search([('x_applicant_id','=',apdata.id)])
        #prev_renewal = http.request.env['x_renewal_history'].sudo().search([('x_applicant_id','=',apdata.id)])
        #card = http.request.env['x_card_history'].sudo().create(c_history)
        renewal = http.request.env['x_renewal_history'].sudo().create(re_history)
        ap_value = { 'partner_phone': phone, 'x_address_en': address , 'x_address_mm': address_mm, 'x_photo': x_photo ,'x_state': 22 }
        apdata.sudo().write(ap_value)
        return http.request.redirect('/my_renewal_list')

    @http.route(['/renewal_lists','/renewal_lists/page/<int:page>'], type='http', auth='public', website=True)
    def renewal_lists(self, page=1):
        renewal_data = http.request.env['hr.applicant'].sudo().search([('x_state','=',22)],offset=(page-1)*20, limit=20)
        total = http.request.env['hr.applicant'].sudo().search_count([('x_state','=',22)])
        pager = request.website.pager( url = '/renewal_lists', total = total, page=page, step = 20, scope = 5)
        position = 'all'
        appdata = http.request.env['hr.job'].sudo().search([])
        paydata = http.request.env['x_payment_type'].sudo().search([('x_form_type','=','Second')])
        return http.request.render('website.renewal-lists', {'renewal_data':renewal_data,'position':position,'pager':pager, 'paydata':paydata, 'appdata':appdata})

    @http.route(['/renewal_lists_detail','/renewal_lists_detail/page/<int:page>'], type='http', auth='public', website=True, methods=['POST'])
    def renewal_lists_detail(self, page=1, **post):
        pay_status = post.get('x_pay_status')
        name = post.get('x_search')
        #if name:
           #id = int(name)
        if not pay_status and not name:
           return http.request.redirect('/renewal_lists')
        if pay_status and not name:
           #renewal_data = []   
           #total = 0
           #aapdata = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_payment_status','=',pay_status),('x_application_payment_id','=',)])
           #renewal_apdata = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',22),('x_renewal_payment','=',pay_stauts)])
           #for redata in renewal_apdata:
               #aapays = redata.x_applicant_application_payment
               #for aapay in aapays:
           renewal_data = http.request.env['x_applicant_application_payment'].sudo().search(['&','&',('x_renew_status','=',True),('x_payment_status','=',pay_status),'|','|',('x_application_payment_id','=',77),('x_application_payment_id','=',78),('x_application_payment_id','=',61)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_applicant_application_payment'].sudo().search_count(['&','&',('x_renew_status','=',True),('x_payment_status','=',pay_status),'|','|',('x_application_payment_id','=',77),('x_application_payment_id','=',78),('x_application_payment_id','=',61)])

                   #if aapay.x_payment_status == pay_status and aapay.x_application_payment_id.x_payment_id.id == 13:
                      #renewal_data.append(redata)
                      #total +=1
           #total = http.request.env['hr.applicant'].sudo().search_count([('x_state','=',22)])
        if name and not pay_status:
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',22),'|','|',('x_approval_no','ilike',name),('name','ilike',name),('id','like',name)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',22),'|','|',('x_approval_no','ilike',name),('name','ilike',name),('id','like',name)])
        if pay_status and name:
           renewal_data = http.request.env['hr.applicant'].sudo().search(['&',('x_state','=',22),'|','|',('x_approval_no','ilike',name),('name','ilike',name),('id','like',name)],offset=(page-1)*20, limit=20)
           total = http.request.env['hr.applicant'].sudo().search_count(['&',('x_state','=',22),'|','|',('x_approval_no','ilike',name),('name','ilike',name),('id','like',name)])
        pager = request.website.pager( url = '/renewal_lists_detail', total = total, page=page, url_args= post,step =20, scope = 4,)
        return http.request.render('website.renewal-lists', {'renewal_data':renewal_data,'pager':pager,'pay_status':pay_status,'name':name,'total':total})

    @http.route(['/remind_renewal'], type='http', auth='public', methods=['POST'], website=True)
    def remind_renewal(self, **post):
        id = post.get('id')
        remark = post.get('x_renew_remark')
        todaydate =  fields.Datetime.now()
        apdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        val = {'x_renew_state':1}
        apdata.sudo().write(val)
        useremail = apdata.email_from        
        reg_no = apdata.x_reg_no
        regno = str(reg_no)
        jobname = apdata.job_id.name
        job_name = jobname.lower()
        aid = str(id)
        dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','review')])
        durl = dynamic_url.x_name
        url = durl+job_name+'?id='+aid
        if remark:
           message = "Your need to renewal your form at "+url+" and "+regno+"  and remark "+remark+"."
        if not remark:
           message = "Your need to renewal your form at "+url+" and "+regno
        subject = "Remind Renew Application"
        y = send_email(useremail,message,subject)
        if y["state"]:
           jobname = apdata.job_id.name
           url = jobname.lower()+'-registration-list'
           return http.request.redirect(url)
        if not y["state"]:
           return request.redirect('/home')


    @http.route(['/confirm_renewal'], type='http', auth='public', methods=['POST'], website=True)
    def confirm_renewal(self, **post):
        id = post.get('id')
        payid = post.get('form_type')
        pay_id = int(payid)
        remark = post.get('x_remark')
        todaydate =  fields.Datetime.now()
        apdata = http.request.env['hr.applicant'].sudo().search([('id','=',id)])
        apay = http.request.env['x_application_payment'].sudo().search(['&',('x_payment_id','=',pay_id),('x_application_id','=',apdata.job_id.id)])
        aapay = http.request.env['x_applicant_application_payment'].sudo().search(['&',('x_applicant_id','=',apdata.id),('x_application_payment_id','=',apay.id)])
        if aapay:
           return http.request.redirect('/home')
        if not aapay:
           pay_value = { 'x_renew_status':True,'x_applicant_id': apdata.id, 'x_application_payment_id': apay.id, 'x_payment_status': 'Pending', 'x_remark': remark ,'x_job_id':apdata.job_id.id,'x_partner_id':apdata.partner_id.id,'x_apply_date': todaydate }
           Pay = http.request.env['x_applicant_application_payment'].sudo().create(pay_value)
           apid = Pay.id
           aaid1 = str(apid)
           useremail = apdata.email_from
           dynamic_url = http.request.env['x_dynamic_url'].sudo().search([('x_type','=','review')])
           url = dynamic_url.x_name
           if remark:
              message = "Your renewal form is accepted and please pay payment "+url+aaid1+" and remark "+remark+"."
           if not remark:
              message = "Your renewal form is accepted and please pay payment "+url+aaid1
           subject = "Renew Application"
           y = send_email(useremail,message,subject)
           if y["state"]:
              return http.request.redirect('/renewal_lists')
           if not y["state"]:
              return request.redirect('/home')

    @http.route('/renewal_card', type='http', auth="public", methods=['POST'], website=True)
    def renewal_card(self, **post):
        aid1 = post.get('id')
        aid = int(aid1)
        #par_id = request.env.user.partner_id.id
        #aapay = http.request.env['x_applicant_application_payment'].sudo().search([('x_applicant_id','=',aid)])
        apdata = http.request.env['hr.applicant'].sudo().search([('id','=',aid)])
        card = http.request.env['x_card'].sudo().search([('x_applicant_id','=',aid)])
        c_value = { 'x_reg_no': apdata.x_reg_no,'x_start_date': card.x_start_date, 'x_expire_date': card.x_expire_date, 'x_applicant_id': card.x_applicant_id.id, 'x_application_id': card.x_application_id.id }
        cdata = http.request.env['x_card_history']
        cdata.sudo().create(c_value)
        type = post.get('job_type')
        ycount = post.get('x_total_year')
        year_count = int(ycount)
        date =  fields.Datetime.now()
        new_date1 = date + relativedelta(years=year_count)
        new_date = new_date1.date()
        val = {
                'x_card_reg_no':post.get('x_card_reg_no'),
                'x_applicant_id': apdata.id,
                'x_application_id': apdata.job_id.id,
                'x_start_date': post.get('x_start_date'),
                'x_expire_date': post.get('x_expire_date'),
                'x_remark': post.get('x_confirm_remark'),
                'x_total_year': year_count,
                'x_form_type': post.get('form_type'),
                'x_issue_card': '',
              }
        res = card.sudo().write(val)
        if res:
           state = {'x_state':10}
           apdata.sudo().write(state)
           jobid = apdata.job_id.id
           useremail = apdata.email_from
           message = "Your renewal card can be issued"
           subject = "Card Renew"
           y = send_email(useremail,message,subject)
           if y["state"]:
              if jobid == 1:
                 return http.request.redirect('/pe-renew-list')
              if jobid == 5:
                 return http.request.redirect('/rsec-renew-list')
              if jobid == 6:
                 return http.request.redirect('/rle-renew-list')
              if jobid == 8:
                 return http.request.redirect('/rfpe-renew-list')
              if jobid == 10:
                 return http.request.redirect('/rec-renew-list')
           if not y["state"]:
               return http.request.redirect('/home')

    @http.route(['/payment_type_detail','/payment_type_detail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def payment_type_detail(self, page=1,**post):
        x_job_type = post.get('x_job_type')
        if x_job_type:
           type=int(x_job_type)
           apdata=http.request.env['x_application_payment'].sudo().search(['&',('x_amount','!=',0),('x_application_id','=',type)], offset=(page-1)*20, limit=20)
           total=http.request.env['x_application_payment'].sudo().search_count(['&',('x_amount','!=',0),('x_application_id','=',type)])
           pager = request.website.pager( url = '/payment_type_detail', total = total, page=page, url_args= post,step = 20, scope = 4)
           jobdata = http.request.env['hr.job'].sudo().search(['&','&','&',('id','!=',13),('id','!=',14),('id','!=',16),('id','!=',29)])
           return http.request.render('website.application-payment-records',{'aprecords':apdata, 'pager':pager, 'jobdata':jobdata, 'jobtype':x_job_type})
        if not x_job_type:
           return http.request.redirect('/application-payment-records')

    @http.route(['/discipline-list','/discipline-list/page/<int:page>'], type='http', auth='public', website=True)
    def disciplinelist(self, page=1):
        predata = http.request.env['x_discipline_list'].sudo().search([])
        total = http.request.env['x_discipline_list'].sudo().search_count([])
        pager = request.website.pager( url = '/discipline-list', total = total, page=page, step = 20, scope = 4)
        jobdata = http.request.env['hr.job'].sudo().search([])
        discipline=http.request.env['x_discipline'].sudo().search([])
        position = 'all'
        return http.request.render('website.discipline-list',{'jobdata':jobdata,'predata':predata,'discipline':discipline,'pager':pager,'position':position}) 

    @http.route('/discipline-entry', type='http', auth='public', website=True)
    def discipline_entry(self, **kw):
        id = kw.get('id')
        predata = http.request.env['x_discipline_list'].sudo().search([('id','=',id)])
        jobdata = http.request.env['hr.job'].sudo().search([])
        lid = http.request.env['x_discipline_list'].sudo().search([], order="id desc", limit=1)
        return http.request.render('website.discipline-entry',{'lid':lid,'jobdata':jobdata,'predata':predata})

    @http.route(['/save_discipline/'], type='http', auth='public', website=True, methods=['POST'])
    def save_discipline(self, **post):
        id = post.get('id')
        predata = http.request.env['x_discipline_list']
        jobdata = http.request.env['hr.job'].sudo().search([])
        val = {
               'x_description': post.get('x_description'),
               'x_dis_type': post.get('x_dis_type'),
               'x_name': post.get('x_name')               
              }
        predata.sudo().create(val)
        return http.request.redirect('/discipline-list')
       # return http.request.render('website.discipline-list',{'predata':predata,'jobdata':jobdata})
    
    @http.route(['/desciplinedetail','/desciplinedetail/page/<int:page>'], type='http', auth="public", method=['POST'], website=True, csrf=False)
    def discipline_detail(self, page=1,**post):
        code = post.get('code') 
        dis_type=post.get('x_dis_type')
        if not dis_type:
           position = 'all'
        if dis_type:
           type = int(dis_type)
           position = 'select'
        jobdata = http.request.env['x_discipline_list'].sudo().search([])
        if code and not dis_type:
           predata = http.request.env['x_discipline_list'].sudo().search([('x_name','ilike',code)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_discipline_list'].sudo().search_count([('x_name','ilike',code)])
        if not code and not dis_type:
           predata = http.request.env['x_discipline_list'].sudo().search([],offset=(page-1)*20, limit=20)
           total = http.request.env['x_discipline_list'].sudo().search_count([])
        if dis_type and not code:
           predata = http.request.env['x_discipline_list'].sudo().search([('x_dis_type','=',type)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_discipline_list'].sudo().search_count([('x_dis_type','=',type)])
        if code and dis_type:
           predata = http.request.env['x_discipline_list'].sudo().search(['&',('x_name','ilike',code),('x_dis_type','=',type)],offset=(page-1)*20, limit=20)
           total = http.request.env['x_discipline_list'].sudo().search_count(['&',('x_name','ilike',code),('x_dis_type','=',type)])
        pager = request.website.pager( url = '/desciplinedetail', total = total, page=page,url_args= post, step = 20, scope = 4)
        return http.request.render('website.discipline-list',{'predata':predata,'jobdata':jobdata,'type':dis_type,'pager':pager,'position':position,'code':code})


    @http.route(['/payment_new'], type='http', auth='public', website=True, csrf=False)
    def _pay(self, **post):
        payment_description = 'MIT'
        currency = 'MMK'
        total = 1000
        app_order_id = post.get('oid')
        app_id = 'mec'
        p_method = '2C2P'
        user_defined_1 = post.get('name')
        datas = {
                 "payment_description":payment_description,
                 "currency":currency,
                 "total":total,
                 "app_order_id":app_order_id,
                 "app_id":app_id,
                 "p_method":p_method,
                 "user_defined_1":user_defined_1
                 }
        headers = {'content-type': 'application/json'}
        url = "http://13.76.81.55:8080/gateway/api/v1/savePayment"
        response = requests.post(url, data=json.dumps(datas), headers=headers)
        y = response.json()
        if y["state"]:
            return request.redirect(y["url"])

    @http.route('/mpu_success', type='http', auth='public', website=True)
    def mpu_suc(self, **kw):
        return http.request.render('website.mpusuccess')

