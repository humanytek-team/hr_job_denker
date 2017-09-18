# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

SELECTION = [('Bajo','Bajo'),
            ('Insuficiente','Insuficiente'),
            ('Regular','Regular'),
            ('Suficiente','Suficiente'),
            ('Alto','Alto'),
            ('NA','NA')]

class HrJobSubordinateLine(models.Model):
    _name = "hr.job.subordinate.line"

    job_id = fields.Integer('job_id', required=True, ondelete='cascade')
    puesto_id = fields.Many2one('hr.job','Puesto', domain="[('padre_id', '=', False)]", required=True)

    @api.model
    def create(self, values):
        #print 'subordinate_create'
        #print 'context: ',self._context
        puesto = self.env['hr.job'].search([('id','=',values['puesto_id'])])
        record = super(HrJobSubordinateLine, self).create(values)

        #if self._context.get('f', False) == False:
        puesto.padre_id = record.job_id
        return record

    # def write(self, values):
    #     #print 'subordinate_write'
    #     self.puesto_id.padre_id = False
    #     puesto = self.env['hr.job'].search([('id','=',values['puesto_id'])])
    #     record = super(HrJobSubordinateLine, self).write(values)

    #     #if self._context.get('f', False) == False:
    #     puesto.padre_id = self.job_id
    #     return record

    @api.one
    def unlink(self):
        #print 'subordinate_unlink'
        puesto = self.puesto_id

        #if self._context.get('f', False) == False:
        puesto.padre_id = False
        return super(HrJobSubordinateLine, self).unlink()



class HrJobFunctionLine(models.Model):
    _name = "hr.job.function.line"

    job_id = fields.Integer('job_id', required=True, ondelete='cascade')
    funcion = fields.Char('Funcion', required=True)


class HrJobKnowledgeLine(models.Model):
    _name = "hr.job.knowledge.line"

    job_id = fields.Integer('job_id', required=True, ondelete='cascade')
    conocimiento = fields.Char('Conocimiento', required=True)


# class HrToolLine(models.Model):
#     _name = "hr.job.tool.line"

#     job_id = fields.Integer('job_id', required=False, ondelete='cascade')
#     herramienta = fields.Char('Herramienta', required=False)


class HrJobCommentLine(models.Model):
    _name = "hr.job.comment.line"

    job_id = fields.Integer('job_id', required=True, ondelete='cascade')
    comentario = fields.Char('Comentario', required=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    #SOBRESCRITURA DE CAMPO PARA AGREGAR DOMINIO
    job_id = fields.Many2one('hr.job', string='Job Title', domain="[('state', 'in', ['authorized','recruit','open'])]" )


class HrJob(models.Model):
    _inherit = 'hr.job'

    @api.multi
    def authorize(self):
        vals = {}
        vals['state'] = 'authorized'
        #vals['authorized'] = True
        self.write(vals)
        return True

    @api.multi
    def unauthorize(self):
        vals = {}
        vals['state'] = 'unauthorized'
        #vals['authorized'] = False
        self.write(vals)
        return True

    @api.multi
    def start(self):
        vals = {}
        vals['state'] = 'recruit'
        self.write(vals)
        return True

    #authorized = fields.Boolean('Autorizado', default=False)
    #REMPLAZA EL CAMPO ORIGINAL Y AGREGA LOS ESTADOS unauthorized y authorized
    state = fields.Selection([
        ('unauthorized', 'Puesto no autorizado'),
        ('authorized', 'Puesto autorizado'),
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')],
        string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='unauthorized', help="Set whether the recruitment process is open or closed for this job position.")


    @api.model
    def create(self, values):
        #print 'create'

        #DE EXISTIR ELIMINA LAS LINEAS DUPLICADAS EN SUBORDINADO_IDS
        if 'subordinado_ids' in values:
            k = values['subordinado_ids']
            k = sorted(k)
            dedup = [k[i] for i in range(len(k)) if i == 0 or k[i] != k[i-1]]
            values['subordinado_ids'] = dedup
        record = super(HrJob, self).create(values)
        return record

    def write(self, values):
        #print 'write'
        #DE EXISTIR ELIMINA LAS LINEAS DUPLICADAS EN SUBORDINADO_IDS
        if 'subordinado_ids' in values:
            k = values['subordinado_ids']
            #print k
            k = sorted(k)
            dedup = [k[i] for i in range(len(k)) if i == 0 or k[i] != k[i-1]]
            #print dedup
            values['subordinado_ids'] = dedup



        return super(HrJob, self).write(values)

    def unlink(self):
        #print 'unlink'
        puesto_hijos = self.env['hr.job'].search([('padre_id','=',self.id)])
        for hijo in puesto_hijos:
            hijo.padre_id = False

        subordinado_line = self.env['hr.job.subordinate.line'].search([('puesto_id','=',self.id)])
        subordinado_line.unlink()
        return super(HrJob, self).unlink()

    #HERENCIA DE METODO DE HR_RECRUITMENT QUE GENERA ERROR
    @api.one
    def _compute_application_count(self):
        #print '_compute_application_count EX'
        #print 'self: ',self
        # print '_context: ',self._context
        # if len(self) > 1:
        #     if self[0].padre_id.id == self[1].id:
        #         self = self[0]
        #     elif self[1].padre_id.id == self[0].id:
        #         self = self[1]
        super(HrJob, self)._compute_application_count()


    padre_id = fields.Many2one('hr.job','Puesto a quien reporta', readonly=1,store=True,)
    subordinado_ids = fields.One2many('hr.job.subordinate.line', 'job_id', 'Puestos a su cargo')

    #FUNCIONES DEL AREA
    funcion_ids = fields.One2many('hr.job.function.line', 'job_id', 'Funciones del area')


    #PERFIL
    sexo = fields.Selection(
            [('Masculino','Masculino'),
            ('Femenino','Femenino'),
            ('Indistinto','Indistinto')],
            'Sexo', default='Indistinto')

    estado_civil = fields.Selection(
            [('Casado','Casado'),
            ('Soltero','Soltero'),
            ('Union libre','Union libre'),
            ('Otro','Otro')],
            'Estado civil', default='Indistinto')
    educacion = fields.Char('Educacion',)
    experiencia = fields.Char('Experiencia en el puesto',)
    edad = fields.Char('Edad',)
    idioma = fields.Char('Idioma',)
    licencia = fields.Char('Licencia',)

    #CONOCIMIENTOS PREVIOS
    conocimiento_ids = fields.One2many('hr.job.knowledge.line', 'job_id', 'Conocimientos previos')


    #PSICOMETRIAS
    analisis_problemas = fields.Selection(SELECTION,'Analisis de problemas')
    toma_decisiones = fields.Selection(SELECTION,'Toma de decisiones')
    juicio = fields.Selection(SELECTION,'Juicio')
    comunicacion = fields.Selection(SELECTION,'Comunicacion')
    liderazgo = fields.Selection(SELECTION,'liderazgo')
    delegacion = fields.Selection(SELECTION,'Delegacion')
    desarrollo_colaboradores = fields.Selection(SELECTION,'Desarrollo de colaboradores')
    trabajo_equipo = fields.Selection(SELECTION,'Trabajo en equipo')
    inteligencia_emocional = fields.Selection(SELECTION,'Inteligencia emocional')
    tolerancia_presion = fields.Selection(SELECTION,'Tolerancia a la presion')
    actitud_servicio = fields.Selection(SELECTION,'Actitud de servicio')
    seguimiento = fields.Selection(SELECTION,'Seguimiento y control')
    planeacion = fields.Selection(SELECTION,'Planeacion y organizacion')
    enfoque_resultados = fields.Selection(SELECTION,'Enfoque a resultados')
    indice_confianza = fields.Selection(SELECTION,'Indice de confianza')
            
    ci = fields.Selection([('Inferior','Inferior'),
            ('Suficiente','Suficiente'),
            ('Alto','Alto'),
            ('NA','NA')],'CI')

    #EQUIPO BAJO TU RESPONSABILIDAD
    computadora = fields.Selection(
            [('Laptop','Laptop'),
            ('PC','PC'),],
            'Computadora')
    dominio_computadora = fields.Selection(
            [('Basico','Basico'),
            ('Medio','Medio'),
            ('Alto','Alto'),
            ('Experto','Experto'),],
            'Dominio de computadora')

    telefono_fijo = fields.Selection(
            [('Basico','Basico'),
            ('Avanzado','Avanzado'),],
            'Telefono fijo')
    telefono_celular = fields.Selection(
            [('Basico','Basico'),
            ('Medio','Medio'),
            ('Avanzado','Avanzado'),],
            'Telefono celular')

    correo = fields.Selection(
            [('Gmail','Gmail'),
            ('Local','Local'),],
            'Correo electronico')
    tipo_correo = fields.Selection(
            [('Generico','Generico'),
            ('Personalizado','Personalizado'),],
            'Tipo correo electronico')

    muebles = fields.Selection(
            [('Grande','Grande'),
            ('Estandar','Estandar'),],
            'Muebles de oficina')

    muebles_opciones = fields.Selection(
            [('Silla','Silla'),
            ('Escritorio','Escritorio'),
            ('Cajonera','Cajonera'),],
            'Opciones de muebles')
    # silla = fields.Boolean('Silla',)
    # escritorio = fields.Boolean('Escritorio',)
    # cajonera = fields.Boolean('Cajonera',)

    uniforme = fields.Selection(
            [('Admin','Admin'),
            ('Operativos','Operativos'),],
            'Uniforme')


    uniforme_opciones = fields.Selection(
            [('Camisa','Camisa'),
            ('Zapato','Zapato'),
            ('Faja','Faja'),
            ('Bata','Bata'),],
            'Opciones de niforme')
    # camisa = fields.Boolean('Camisa',)
    # zapato = fields.Boolean('Zapato ind.',)
    # faja = fields.Boolean('faja',)
    # bata = fields.Boolean('Bata/Mandil',)

    tarjeta_presentacion = fields.Boolean('Tarjeta de presentacion',)
    firma = fields.Boolean('Firma electronica',)


    caja_chica = fields.Boolean('Caja Chica',)
    vehiculo = fields.Boolean('Vehiculo',)
    tarjeta_gasolina = fields.Boolean('Tarjeta de gasolina',)
    tarjeta_viaticos = fields.Boolean('Tarjeta de viaticos',)
    tarjeta_iave = fields.Boolean('Tarjeta IAVE',)

    #herramienta_ids = fields.One2many('hr.job.tool.line', 'job_id', 'Otras herramientas')
    herramientas = fields.Text('Otras Herramientas')


    #SOFTWARE NECESARIOS
    microsoft_office = fields.Boolean('Microsoft Office',)
    autocad = fields.Boolean('Autocad o Solid Works',)
    captive = fields.Boolean('Captive',)
    ilustrador = fields.Boolean('Ilustrador',)
    photoshop = fields.Boolean('Photoshop',)
    nitro = fields.Boolean('Nitro',)
    visio = fields.Boolean('Project Visio',)
    sql_server = fields.Boolean('Sql Server',)
    reporteador = fields.Boolean('Reporteador',)
    ms_office = fields.Boolean('MS Office',)

    #ACCESOS SOFTWARE INTERNO
    compaq = fields.Boolean('Compaq',)
    nomipaq = fields.Boolean('Nomiopaq',)
    acceso_remoto = fields.Boolean('Acceso remoto',)
    tel_restringido = fields.Boolean('Telefono restringido celular y LD',)
    confirmador = fields.Boolean('Confirmador',)
    costeador = fields.Boolean('Costeador',)
    universidad_denker = fields.Boolean('Universidad Denker',)

    #RED
    red_compras = fields.Boolean('Compras',)
    red_gerencia = fields.Boolean('Gerencia',)
    red_lider = fields.Boolean('Lider',)
    red_produccion = fields.Boolean('Produccion',)
    red_proyectos = fields.Boolean('C: Proyectos',)
    red_bancos = fields.Boolean('Bancos',)
    red_contabilidad = fields.Boolean('Contabilidad',)
    red_contraloria = fields.Boolean('Contraloria',)
    red_cxp = fields.Boolean('CXP',)
    red_cxc = fields.Boolean('CXC',)
    red_nominas = fields.Boolean('Nominas',)
    red_rh = fields.Boolean('R. Humanos',)
    red_abastos = fields.Boolean('Abastos',)
    red_mkt = fields.Boolean('MKT',)
    red_sistemas = fields.Boolean('Sistemas',)

    red_ventas = fields.Boolean('Ventas',)
    red_sc = fields.Boolean('SC',)
    red_logistica = fields.Boolean('Logistica',)
    red_sucursales = fields.Boolean('Sucursales',)
    red_desarrollo = fields.Boolean('Desarrollo',)
    red_disenio = fields.Boolean('Diseño',)
    red_cotizaciones = fields.Boolean('Cotizaciones',)
    red_proyectod = fields.Boolean('Proyectos',)
    red_oc = fields.Boolean('OC',)

    #ERP
    # erp_ventas = fields.Boolean('Ventas',)
    # erp_automatizacion = fields.Boolean('Automaticacion de las oportunidades',)
    # erp_proyecto = fields.Boolean('Proyecto',)
    # erp_inventario = fields.Boolean('Inventario',)
    # erp_calidad = fields.Boolean('Calidad',)
    # erp_fabricacion = fields.Boolean('Fabricacion',)
    # erp_compras = fields.Boolean('Compras',)
    # erp_vacaciones = fields.Boolean('Vacaciones',)
    # erp_procesos_seleccion = fields.Boolean('Procesos de seleccion',)
    # erp_partes_horas = fields.Boolean('Partes de horas',)
    # erp_helpdesk = fields.Boolean('Helpdesk',)
    # erp_evaluaciones = fields.Boolean('Evaluaciones',)
    # erp_enviar_email = fields.Boolean('Enviar Email',)
    # erp_planificacion = fields.Boolean('Planificacion',)
    # erp_sitio_web = fields.Boolean('Sitio Web',)
    # erp_conocimiento = fields.Boolean('Conocimiento',)
    # erp_administracion = fields.Boolean('Administracion',)
    # erp_fecha_faturae = fields.Boolean('Fecha de FacturaE',)
    # erp_facturacion_e = fields.Boolean('Facturacion Electronica de Mexico',)

    erp_ventas = fields.Selection(
            [('Usuario: documentos propios','Usuario: documentos propios'),
            ('Usuario: todos los documentos','Usuario: todos los documentos'),
            ('Responsable','Responsable'),],
            'Ventas')
    erp_automatizacion = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Automatizacion de procesos')
    erp_proyecto = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Proyecto')
    erp_inventario = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Inventario')
    erp_fabricacion = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Fabricacion')
    erp_calidad = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Calidad')
    erp_contabilidad = fields.Selection(
            [('Facturacion','Facturacion'),
            ('Contable','Contable'),
            ('Asesor','Asesor'),],
            'Contabilidad')
    erp_compras = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Compras')
    erp_vacaciones = fields.Selection(
            [('Oficial','Oficial'),
            ('Responsable','Responsable'),],
            'Vacaciones')
    erp_procesos_seleccion = fields.Selection(
            [('Oficial','Oficial'),
            ('Responsable','Responsable'),],
            'Procesos de seleccion')
    erp_partes_horas = fields.Selection(
            [('Oficial','Oficial'),],
            'Partes de horas')
    erp_helpdesk = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Helpdesk')
    erp_evaluaciones = fields.Selection(
            [('Oficial','Oficial'),
            ('Responsable','Responsable'),],
            'Evaluaciones')    
    erp_enviar_email = fields.Selection(
            [('Usuario','Usuario'),],
            'Enviar Email')
    erp_planificacion = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Planificacion')
    erp_sitio_web = fields.Selection(
            [('Restricted editor','Restricted editor'),
            ('Editor y disenador','Editor y diseñador'),],
            'Sitio Web')
    erp_conocimiento = fields.Selection(
            [('Usuario','Usuario'),],
            'Conocimiento')
    erp_administracion = fields.Selection(
            [('Permisos de acceso','Permisos de acceso'),
            ('Configuracion','Configuracion'),],
            'Administracion')
    erp_fecha_faturae = fields.Selection(
            [('Date','Date'),
            ('Fecha/Hora','Fecha/Hora'),],
            'Fecha FacturaE')
    erp_facturacion_e = fields.Selection(
            [('Usuario','Usuario'),
            ('Responsable','Responsable'),],
            'Facturacion ElectronicaE')

    #SIIL #QUITAR
    # siil_direccion = fields.Boolean('Direccion',)
    # siil_clientes = fields.Boolean('Clientes',)
    # siil_proveedores = fields.Boolean('Proveedores',)
    # siil_articulos = fields.Boolean('Articulos',)
    # siil_personal = fields.Boolean('Personal',)
    # siil_almacen = fields.Boolean('Almacen/Compras',)
    # siil_produccion = fields.Boolean('Produccion',)
    # siil_ventas = fields.Boolean('Ventas',)
    # siil_cxp = fields.Boolean('CXP',)

    #INTRANET QUITAR
    # intranet_direccion = fields.Boolean('Direccion',)
    # intranet_catalogos = fields.Boolean('Catalogos',)
    # intranet_operacion = fields.Boolean('Operacion',)
    # intranet_sc = fields.Boolean('Servicio al cliente',)
    # intranet_ventas = fields.Boolean('Ventas',)
    # intranet_mkt = fields.Boolean('MKT',)
    # intranet_finanzas = fields.Boolean('Finanzas',)
    # intranet_sgcd = fields.Boolean('SGCD',)
    # intranet_mesa_ayuda = fields.Boolean('Mesa de ayuda',)

    comentarios_extra = fields.Text('Comentarios extra')

    #COMENTARIOS FINALES
    comentario_ids = fields.One2many('hr.job.comment.line', 'job_id', 'Comentarios')