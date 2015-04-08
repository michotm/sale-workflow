# -*- coding: utf-8 -*-
from openerp import fields, models , api
import pdb;
from openerp import http

class SaleLineGeneratorFrom(http.Controller):
    _name='sale.line.generator.from'
    _inherit='sale.generator'
    

    
    def _prepare_partner_vals(self,name,street,email,phone,city,state,key):
         return {
             'name': name,
	     'street':street,
	     'email' :email,
	     'phone':phone,
	     'city' :city,
	     'state' :state,
	     'zip' :key,
	      
         }
	 
    def _prepare_generator_vals(self,name):
         return {
             ' partner_ids.name': name,
         }

    def _css(self):
	css="""
	
	"""
	return css
    
   

    @http.route('/<int:id>/', type="http")
    def index(self,id, **kw):
	valeur=id
	
	temp = """
	<!DOCTYPE HTML>
  <html>
  <head>
    <meta charset="utf-8">
    <link href="/sale_generator_web/static/src/css/bootstrap.css" rel="stylesheet" type="text/css" >
    <link href="/sale_generator_web/static/src/css/sale_generator0.css" rel="stylesheet " type="text/css" >
    <script src="/sale_generator_web/static/src/js/bootstrap.js"></script>
    <script src="/sale_generator_web/static/src/js/jquery.js"></script> 
  
  </head>
<body>
 <div class="container">
      <nav class="navbar navbar-inverse">
        <div class="container-fluid">
        </div>
      </nav>

      <header class="page-header">
      <h1> Formulaire </h1>
      </header>
          <div class="row">
            <div class="col-md-5 col-md-offset-1">
                <div class="content">
                  <div class="pull-middle">
                    <p class="lead">Ajouter les informations </p>
                    <div class="panel panel-default">
                        <div class="panel-body">
                            <form method="post" action="/sale_generator" role="form">
                                <div class="input-group">
                                    <input type="name" name="nom" class="form-control" placeholder="Nom" required onFocus="javascript:this.value="">
				     <input type="Email" name="email" class="form-control" placeholder="Email" required>
				     <input type="Phone" name="phone" class="form-control" placeholder="Mobile" required>
				     <input type="Address" name="street" class="form-control" placeholder="La Rue" required>
				     <input type="Address" name="city" class="form-control" placeholder="La ville" required>
				     <input type="Address" name="state" class="form-control" placeholder="Le pays" required>
				     <input type="Address" name="zip" class="form-control" placeholder="Le code postal" required>
                                     <input type="HIDDEN" name="id" value = {}><br>
                                      <button class="btn btn-primary pull-right" type="submit" onclick="clicbutton()" >Enregistrer</button> 
                                </div>
                            </form>
                        </div>
                    </div>
                  </div>              
            </div>
          </div>
            
            <div class="col-md-4 col-md-offset-2 ">
                <div class="phone">
                    <img class="img-responsive img-rounded" src="/sale_generator_web/static/src/images/test.png">
                </div>
            </div>
           </div>
          </div>
  </body>
</html>
	"""
        return (temp.format(valeur))


    @http.route('/sale_generator/', type="http")
    def clicbutton(self,**kw):
        res_partner_obj = http.request.env['res.partner']
	print '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	generator_obj = http.request.env['sale.generator']
	generator = generator_obj.browse(int(kw['id']))
        vals=self._prepare_partner_vals(kw['nom'],kw['street'],kw['email'],kw['phone'],kw['city'],kw['state'],kw['zip'])
        partner = res_partner_obj.create(vals)
	print partner.id
	generator.write({'partner_ids':[(4,partner.id,0)]})
	import pdb; pdb.set_trace()
	print 'kw',kw
