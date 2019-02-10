# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
import random
#ver la importación de tools de odoo, arriba importada
from odoo.exceptions import ValidationError
import logging
#from datetime import datetime, timedelta
import datetime

from odoo.service import model

_logger = logging.getLogger(__name__)







class city(models.Model):
    _name = 'hotels_be_bago.city'
    name = fields.Char()
    description = fields.Text()
    ubication = fields.Char(String="Ubication")
    country = fields.Many2one("res.country", "Pais")
    imagenpais=fields.Binary(related="country.image",store=True)
    hotellist = fields.One2many("hotels_be_bago.hotel","ciudad")
    active_id_hotel = fields.Id(related='hotellist.id')

class hotel(models.Model):
    _name = 'hotels_be_bago.hotel'
    name = fields.Char()
    galeriaFotos = fields.Many2many("hotels_be_bago.hotelfotos")
    fotoprincipal=fields.Binary(compute='_recuperar_foto',store=True)
    description = fields.Text()
    ciudad=fields.Many2one("hotels_be_bago.city","Ciudad")
    country=fields.Char(string='Pais del hotel',related='ciudad.country.name',store=True,readOnly=True)
    roomlist=fields.One2many("hotels_be_bago.habitacion","hotel")
    active_id_room = fields.Id(related='roomlist.id')
    estrellas = fields.Selection([('1', '⭐'), ('2', '⭐⭐'), ('3', '⭐⭐⭐'), ('4', '⭐⭐⭐⭐'), ('5', '⭐⭐⭐⭐⭐')])
    valoraciomedia=fields.Selection([('1', '⭐'), ('2', '⭐⭐'), ('3', '⭐⭐⭐'), ('4', '⭐⭐⭐⭐'), ('5', '⭐⭐⭐⭐⭐')],compute='_calcular_media',store=True)
    listaServicios = fields.Many2many("hotels_be_bago.servicis")
    comentarios = fields.One2many('hotels_be_bago.comentarios','hoteles')
    active_id_coment = fields.Id(related='comentarios.id')
    reservas=fields.One2many('hotels_be_bago.reserva','nombrehotel')

    reservaPasadas=fields.One2many('hotels_be_bago.reserva','nombrehotel',compute='_get_reservas_pasadas')
    reservasFuturas = fields.One2many('hotels_be_bago.reserva', 'nombrehotel', compute='_get_reservas_futuras')
    reservasPresentes = fields.One2many('hotels_be_bago.reserva', 'nombrehotel', compute='_get_reservas_presentes')

    @api.one
    @api.depends('reservas')
    def _get_reservas_pasadas(self):
        now=datetime.datetime.now()
        #print("mi id es "+str(self.id))
        self.reservaPasadas  = self.env['hotels_be_bago.reserva'].search([('nombrehotel.id', '=', self.id),
                                                                   ('fechaInicio','<',now),
                                                                   ('fechaFinal','<',now)])
    @api.one
    @api.depends('reservas')
    def _get_reservas_futuras(self):
        now = datetime.datetime.now()
        # print("mi id es "+str(self.id))
        self.reservasFuturas = self.env['hotels_be_bago.reserva'].search([('nombrehotel.id', '=', self.id),
                                                                         ('fechaInicio', '>', now),
                                                                         ('fechaFinal', '>', now)])

    @api.one
    @api.depends('reservas')
    def _get_reservas_presentes(self):
        now = datetime.datetime.now()
        # print("mi id es "+str(self.id))
        self.reservasPresentes = self.env['hotels_be_bago.reserva'].search([('nombrehotel.id', '=', self.id),
                                                                          ('fechaInicio', '<', now),
                                                                          ('fechaFinal', '>', now)])




    @api.depends('comentarios')
    def _calcular_media(self):
        for record in self:

            #print(str(record.name + "tiene "+ str(len(record.comentarios))))
            if len(record.comentarios) > 0:
                arrayComentarios=record.comentarios
                sumaValoracion=0
                media=0
                i=0
                for comentario in arrayComentarios:
                    sumaValoracion=int(sumaValoracion)+int(comentario.valoracion)
                    i=i+1
                media=sumaValoracion/i
                record.valoraciomedia=str(int(media))
            else:
                print("No tiene comentarios por lo que la media se queda en default,1")
                record.valoraciomedia='1'

    @api.depends('galeriaFotos')
    def _recuperar_foto(self):
        for record in self:
            if len(record.galeriaFotos) > 0:
               record.fotoprincipal=record.galeriaFotos[0].foto
            else:
                print("Este hotel no tiene fotos...")
    @api.one
    def anyadir_comentario(self):
        reserva=self.env['hotels_be_bago.reserva'].search([('habitaciones.hotel','=',self.id),('fechaFinal','<=',str(datetime.datetime.today()))])
        #el self.env se usa para recuperar una tabla de la bbdd
        #el search es como usn elect
        comentarios=['Me lo he pasado bien','Buenos efectos audivisuales y atencion al cliente','El baño me ha puesto nervioso', 'J**** donde m***** me he metido tio',"Tocará volver"]

        if len(reserva)!=0:
            cliente={'clientes':reserva[random.randint(0,len(reserva)-1)].clientes.id,'hoteles':self.id,'descripcion':comentarios[random.randint(0,len(comentarios)-1)],'valoracion':str(random.randint(1,5))}
            self.env['hotels_be_bago.comentarios'].create(cliente)
        else:
            print("No se puede crear un comentario porque el hotel no tiene  clientes!")
            return {
                'warning': {
                    'title': "Algo ha ocurrido mal",
                    'message': "No puedes añadir un comentario aleatorio porque este hotel no tiene clientes",
                }
            }
    @api.one
    def anyadir_habitacion(self):
        hotel=self.env['hotels_be_bago.hotel'].search([('id','=',self.id)])
        name="Habitacion " + str(hotel.name) + str(random.randint(1,1000))
        camas=str(random.randint(1,5))
        precios=random.randint(100,1000)
        fotos=self.env['hotels_be_bago.roomfotos'].search([('id','=',random.choice([self.env.ref('hotels_be_bago.roomfoto1').id,self.env.ref('hotels_be_bago.roomfoto2').id,self.env.ref('hotels_be_bago.roomfoto3').id,self.env.ref('hotels_be_bago.roomfoto4').id,self.env.ref('hotels_be_bago.roomfoto5').id]))])

        habitacion={'hotel':hotel.id,'name':name,'camas':camas,'precios':precios,'fotos':[(6,0,fotos.ids)]}
        hotel.roomlist.create(habitacion)
        #print(habitacion)


class habitacion(models.Model):
    _name = 'hotels_be_bago.habitacion'

    hotel = fields.Many2one("hotels_be_bago.hotel", "Hotel")
    name = fields.Text()
    camas = fields.Selection([('1', 'Cama Solitaria'), ('2', 'Cama Matrimonio'), ('3', 'Cama Familiar'),
                                  ('4', 'Cama Infantil con matrimonio'), ('5', 'Distribución numerosa')])
    fotoprincipalRoom = fields.Binary(compute='_recuperar_foto_rooms', store=True)
    fotos = fields.Many2many("hotels_be_bago.roomfotos" , store=True)
    precios = fields.Integer(default=20)
    reserva=fields.One2many("hotels_be_bago.reserva","habitaciones")
    active_id = fields.Id(related='reserva.id')
    disponibilidad=fields.Char(string="Estado",compute='_getestado',readOnly=True)
    descripcion = fields.Text(
            default="Una agradable habitación presidencial. Perfecta para descansar y hacer todo tipo de travesuras.")

    @api.depends('fotos')
    def _recuperar_foto_rooms(self):
        for record in self:
            if len(record.fotos) > 0:
                record.fotoprincipalRoom = record.fotos[0].foto
            else:
                print("Este room no tiene fotos...")

    @api.depends('reserva')
    def _getestado(self):
        for record in self:
            #print(len(record.reserva))
            if(len(record.reserva)>0):
                for valorreserva in record.reserva:
                    if(valorreserva.fechaFinal < str(datetime.datetime.today())):
                        record.disponibilidad="Libre"
                    else:
                        record.disponibilidad="Ocupado"
            else:
                record.disponibilidad="Libre"


class reserva_heredada(models.Model):
    _name='sale.order.line'
    _inherit='sale.order.line'
    reserva=fields.Many2one("hotels_be_bago.reserva","Reservas",store=True)
    nombreHabitacion=fields.Text(related='reserva.habitaciones.name')
    hotel=fields.Many2one(related='reserva.nombrehotel')
    fechaFinalHeredada=fields.Date(related='reserva.fechaFinal')
    fechaInicioHeredada=fields.Date(related='reserva.fechaInicio')
    cantidadReservas = fields.Integer(compute='_compute_len_reserva', store=True)
    fotoHabitacion=fields.Binary(related='reserva.habitaciones.fotoprincipalRoom')

    @api.multi
    @api.depends('reserva')
    def _compute_len_reserva(self):
        for linea in self:
            linea.cantidadReservas = len(linea.reserva)



class reserva_wizard(models.TransientModel):   # La classe és transientModel
     _name = 'hotels_be_bago.reserva_wizard'

     clientes = fields.Many2one("res.partner", "Nombre del cliente")
     city=fields.Many2one("hotels_be_bago.city","Ciudad")
     country=fields.Many2one("res.country","Pais",related='city.country')
     imagenpais=fields.Binary(related='country.image')

     hotel=fields.Many2one("hotels_be_bago.hotel","Hotel")
     descripcion=fields.Text(related='hotel.description')
     fotoprincipalhotel=fields.Binary(related='hotel.fotoprincipal')
     estrellas = fields.Selection([('1', '⭐'), ('2', '⭐⭐'), ('3', '⭐⭐⭐'), ('4', '⭐⭐⭐⭐'), ('5', '⭐⭐⭐⭐⭐')])
     camas = fields.Selection([('1', 'Cama Solitaria'), ('2', 'Cama Matrimonio'), ('3', 'Cama Familiar'),
                                  ('4', 'Cama Infantil con matrimonio'), ('5', 'Distribución numerosa')])
     precios=fields.Integer()
     #es posible que alguien queira hacer varias reservas
     habitacion=fields.Many2many("hotels_be_bago.habitacion","Habitaciones")

     fechaInicio = fields.Date()
     fechaFinal = fields.Date()

     state = fields.Selection([  # El camp state és per a crear l'assistent.
         ('localizacion', "Selecciona Localización"),
         ('hotel', "Selecciona el hotel"),
         ('habitacion', "Selecciona la habitación"),
         ('butaca', "butaca Selection"),
         ('fin', "Fin"),
     ], default='localizacion')


     @api.onchange('clientes','city','estrellas')
     def _continuar_paso_1(self):
         if(self.clientes and  self.city and self.estrellas):

            hoteles=self.env['hotels_be_bago.hotel'].search([('ciudad','=',self.city.id),('estrellas','=',self.estrellas)])
            self.hotel =hoteles
            if(len(self.hotel) > 0 ):
                self.state = 'hotel'
                return {'domain': {'hotel': [('id', 'in', hoteles.ids)]}, }



     @api.onchange('camas', 'precios')
     def _continuar_paso_2(self):
         if (self.camas and self.precios):
             habitaciones = self.env['hotels_be_bago.habitacion'].search(
                 [('precios', '<=', self.precios), ('camas', '=', self.camas),('hotel','in',self.hotel.ids)])
             self.habitacion=habitaciones
             if(len(self.habitacion)>0):
                 self.state='habitacion'
                 return {'domain': {'habitacion': [('id', 'in', habitaciones.ids)]}, }










class reserva(models.Model):
    _name = 'hotels_be_bago.reserva'
    name=fields.Char(string="Nombre de la reserva",compute='_generar_nombre',readonly=True)
    fechaInicio = fields.Date()
    fechaFinal = fields.Date()
    habitaciones = fields.Many2one("hotels_be_bago.habitacion", "Habitacion a reservar")
    clientes = fields.Many2one("res.partner", "Nombre del cliente")
    nombrehotel = fields.Many2one(string='Nombre del hotel', related='habitaciones.hotel', readonly=False, store=True)
    fotocliente=fields.Binary(compute='_get_imagen_cliente',store=True)
    reserva_heredada=fields.One2many("sale.order.line","reserva")
    dias=fields.Float(default=1,compute='_get_number_of_days')


    @api.depends('fechaInicio','fechaFinal')
    def _get_number_of_days(self):
        for record in self:
            if(record.fechaInicio and record.fechaFinal):
                DATETIME_FORMAT = "%Y-%m-%d"
                from_dt = datetime.datetime.strptime(record.fechaInicio, DATETIME_FORMAT)
                to_dt = datetime.datetime.strptime(record.fechaFinal, DATETIME_FORMAT)
                timedelta = to_dt - from_dt
                diff_day = timedelta.days + float(timedelta.seconds) / 86400
                record.dias=diff_day

    @api.one
    def crear_venta(self):
        id_producto=self.env.ref('hotels_be_bago.product2')

        sale_id = self.env['sale.order'].create({'partner_id': self.clientes.id})

        venta={'product_id':id_producto.id,'order_id':sale_id.id,'reserva':self.id,'name':self.name,'product_uom_qty':self.dias,'qty_delivered':1,'qty_invoiced':1,'price_unit':self.habitaciones.precios}
        self.env['sale.order.line'].create(venta)



    @api.one
    def crear_venta_todos(self):
        print("el cliente actual es ")
        print(self.clientes)
        reservasCliente=self.clientes.reservasCli
        print(reservasCliente)
        id_producto = self.env.ref('hotels_be_bago.product2')
        sale_id = self.env['sale.order'].create({'partner_id': self.clientes.id})
        for reserva in reservasCliente:
            venta = {'product_id': id_producto.id, 'order_id': sale_id.id, 'name': reserva.name,'reserva':self.id,
                     'product_uom_qty': reserva.dias, 'qty_delivered': 1, 'qty_invoiced': 1,
                     'price_unit': reserva.habitaciones.precios}
            
            self.env['sale.order.line'].create(venta)


    @api.multi
    @api.depends('habitaciones','fechaInicio','fechaFinal','clientes')
    def _generar_nombre(self):
        for record in self:
            if record.habitaciones and record.fechaInicio and record.fechaFinal and record.clientes:
                    record.name=record.habitaciones.name+' '+record.clientes.name+' '+record.fechaInicio+' '+record.fechaFinal

    @api.depends('clientes')
    def _get_imagen_cliente(self):
        if self.clientes:
            if(self.clientes.image):
                self.fotocliente = self.clientes.image
            if(self.clientes.image_small):
                self.fotocliente = self.clientes.image_small
            if (self.clientes.image_medium):
                self.fotocliente = self.clientes.image_medium

    @api.onchange('fechaInicio','fechaFinal')
    def _manyana(self):
        for record in self:
            if record.fechaFinal and record.fechaInicio:

                fmt='%Y-%m-%d'
                dateInicio=datetime.datetime.strptime(str(record.fechaInicio),fmt)
                dateFinal=datetime.datetime.strptime(str(record.fechaFinal),fmt)
                if dateFinal < dateInicio:
                    record.fechaFinal = dateInicio + datetime.timedelta(days=1)
                    print(record.fechaFinal)
                    return {
                        'warning': {
                            'title': "Algo ha ocurrido mal",
                            'message': "No puedes insertar un dia antes de la fecha de inicio",
                        }
                    }
                else:
                    print(" No hay error!")


            elif record.fechaInicio:
                fmt = '%Y-%m-%d'
                data = datetime.datetime.strptime(str(record.fechaInicio), fmt)
                record.fechaFinal = data + datetime.timedelta(days=1)


               # print(data)

    @api.constrains('fechaInicio', 'fechaFinal')
    def _comprobar_reserva(self):

            for record in self:
                #print(record.habitaciones.id)

                variable = self.search_count([('id', '!=', record.id),('habitaciones.id', '=', record.habitaciones.id) ,('fechaFinal', '>=', record.fechaInicio), ('fechaInicio','<=', record.fechaFinal)])
                variable2=self.search([('id', '!=', record.id),('habitaciones.id', '=', record.habitaciones.id), ('fechaFinal', '>=', record.fechaInicio), ('fechaInicio','<=', record.fechaFinal)])
                print(variable)
                print(variable2)
            for valor in variable2:
                #print(self.name)
                print(valor.name)

            if variable > 0:
                raise ValidationError("Se solapan dos habitaciones \n" + self.name + " con  \n"+valor.name)




class hotelfotos(models.Model):
    _name = 'hotels_be_bago.hotelfotos'
    name = fields.Char("Nombre de la foto")
    foto = fields.Binary("Seleccione una foto para agregar")

class roomfotos(models.Model):
    _name = 'hotels_be_bago.roomfotos'
    name = fields.Char("Nombre de la foto")
    foto = fields.Binary("Seleccione una foto para agregar")

class servicis(models.Model):
    _name = 'hotels_be_bago.servicis'
    name = fields.Char("Nombre del servicio")
    tipo = fields.Selection([('1', 'Higiene personal'), ('2', 'Higiene animal'), ('3', 'Cuidado del vehiculo'),
                                 ('4', 'Descanso'), ('5', 'Comidas y refrigerios')])
    imageser = fields.Binary("Seleccione una foto para el servicio")

class comentarios(models.Model):
    _name='hotels_be_bago.comentarios'
    clientes = fields.Many2one("res.partner", "Nombre del cliente")
    fotocliente=fields.Binary(related='clientes.image')
    namecliente = fields.Char(related='clientes.name')
    hoteles=fields.Many2one('hotels_be_bago.hotel','Hotel')
    descripcion=fields.Text(string="Descripcion")
    valoracion = fields.Selection([('1', '⭐'), ('2', '⭐⭐'), ('3', '⭐⭐⭐'), ('4', '⭐⭐⭐⭐'), ('5', '⭐⭐⭐⭐⭐')],default='5')

class clientes(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    comentariosCli=fields.One2many("hotels_be_bago.comentarios","clientes")
    reservasCli=fields.One2many("hotels_be_bago.reserva","clientes")
    reservasPorPagar=fields.One2many("hotels_be_bago.reserva","clientes" , compute='_generar_reservas_sin_pagar')
    reservasPagadas=fields.One2many("hotels_be_bago.reserva","clientes",compute='_generar_reservas_pagadas')
    tieneReservasPendientes=fields.Boolean(compute='_comprobar_numero_reservas',default=False)

    @api.depends('reservasCli','reservasPorPagar')
    @api.multi
    def _comprobar_numero_reservas(self):
        for record in self:
            if(len(record.reservasPorPagar) > 0 ):
                print(len(record.reservasPorPagar))
                record.tieneReservasPendientes=True
            else:
                record.tieneReservasPendientes=False


    @api.depends('reservasCli')
    @api.multi
    def _generar_reservas_sin_pagar(self):
        for record in self:# por cada cliente...

            if(record.reservasCli):
                reservaPagada = self.env['sale.order.line'].search([]).mapped('reserva')  # obtengo las reservas que tiene una linea de factura
                record.reservasPorPagar=record.reservasCli
                for pagada in reservaPagada: # me dispongo a recorrer las reservas que estan pagadas para ver si son todas las que tiene el usuario self.id

                    if(pagada.clientes.id==record.id):
                        print("Coincidencia")
                        record.reservasPorPagar=record.reservasPorPagar-pagada

    @api.depends('reservasPorPagar')
    @api.multi
    def _generar_reservas_pagadas(self):
        for record in self:
            if(record.reservasCli ):
                    print(len(record.reservasPorPagar))
                    if (len(record.reservasPorPagar)==0):
                        print("entro")
                        record.reservasPagadas=record.reservasCli
                    else:
                        record.reservasPagadas=record.reservasCli-record.reservasPorPagar


    @api.one
    def crear_factura_de_reservas_pendientes(self):
            id_producto = self.env.ref('hotels_be_bago.product2')
            sale_id = self.env['sale.order'].create({'partner_id': self.id})
            for reserva in self.reservasPorPagar:
                venta = {'product_id': id_producto.id, 'order_id': sale_id.id, 'name': reserva.name, 'reserva': reserva.id,
                         'product_uom_qty': reserva.dias, 'qty_delivered': 1, 'qty_invoiced': 1,
                         'price_unit': reserva.habitaciones.precios}

                self.env['sale.order.line'].create(venta)
                self.reservasPorPagar=self.reservasPorPagar-reserva

class wizard_seleccion_reservas(models.TransientModel):
    _name='seleccion.wizard'

    def _default_cliente(self):
        #self._default_pendientes()
        return self.env['res.partner'].browse(self._context.get('active_id'))
        # El context conté, entre altre coses, el active_id del model que està obert.


    cli = fields.Many2one('res.partner', default=_default_cliente , string="Cliente actual")
    cliReservasPendientesOne = fields.One2many(related='cli.reservasPorPagar', string="Reservas por pagar")
    cliReservasPendientesMany = fields.Many2many('hotels_be_bago.reserva',compute='_default_pendientes', string="Reservas por pagar")

    name=fields.Char(name="Nombre de la reserva" , related='cliReservasPendientesOne.name')
    fechaInicio=fields.Date(name="Inicio de la reserva",related='cliReservasPendientesOne.fechaInicio')
    fechaFinal = fields.Date(name="Final de la reserva", related='cliReservasPendientesOne.fechaFinal')
    dias=fields.Float(name="Numero de dias" , related='cliReservasPendientesOne.dias')


    @api.depends('cliReservasPendientesOne')
    @api.multi
    def _default_pendientes(self):
        print("me ejecutooo")
        for record in self:
            print(len(record.cliReservasPendientesOne))
            record.cliReservasPendientesMany=record.cliReservasPendientesMany+record.cliReservasPendientesOne







