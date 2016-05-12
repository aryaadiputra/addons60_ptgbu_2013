{
    'name': 'Product Second Unit of Measure Control and it\'s rate',
    'version': '1.0',
    'category': 'Custom',
    'description': """A module to control second unit of measure and it\'s rate.
    
    For example, if a product has:
    
    - UoM = Sheet
    - 2nd UoM = Kg
    - Rate = 2
    
    Then it means that every 1 sheet of the product = 2 kg
    
    Added :
    
    - DIgabungkan dengan Module ad_purchase_compare
    - Ditambah Untuk Triger Budget
    - Keterangan di lempar ke Notes PO
    - Delegate Field
    - Barang Service Masuk ke Picking
    - Informasi Req By di List Incoming Shipment
    
    """,
    'author': 'ADSOFT',
    'website': 'http://adsoft.co.id',
    'depends': ['base', 'product', 'purchase', 'stock', 'ad_purchase_requisition','ad_material_req'],
    'init_xml': [],
    'update_xml': ['second_uom.xml',],
    'demo_xml': [],
    'installable': True,
    'active': False,
}