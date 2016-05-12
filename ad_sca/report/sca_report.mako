<html>

<head>
<title>AGED PARTNER BALANCE GROUPED BY POP</title>

<style>

	#row_head_line
		{
		font-size:12px;
		border-top-style:solid;
		border-top-width:1px;
		border-top-color:#000;
		
		border-bottom-style:solid;
		border-bottom-width:1px;
		border-bottom-color:#000;
		
		}
	
	.wrap
		{
		height:5mm
		}
	
	.wrap2
		{
		height:25mm;
		width: 40mm;
		font:12px arial,sans-serif;
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		
		border-top-style:solid;
		border-top-width:1px;
		border-top-color:#000;
		
		}
		
	.head_sign
		{
		font:12px arial,sans-serif;
		text-align: center;
		padding:1px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		
		border-top-style:solid;
		border-top-width:1px;
		border-top-color:#000;
		}
		
	.head_left_sign
		{
		font:12px arial,sans-serif;
		text-align: center;
		padding:1px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		
		}
		
	.bottom_sign
		{
		font:12px arial,sans-serif;
		text-align: center;
		padding:1px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		
		border-top-style:solid;
		border-top-width:1px;
		border-top-color:#000;
		
		border-bottom-style:solid;
		border-bottom-width:1px;
		border-bottom-color:#000;
		}
	
	#row_line
		{
		font-size:10px;
		border-top-style:1px;
		border-bottom-style:1px;
		border-left-style:1px;
		border-right-style:1px;
		}
		
	.row_col_left
		{
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		}
		
	.row_col
		{
		
		border-bottom-style:double;
		border-bottom-width:1px;
		border-bottom-color:#000;
		
		}
		
	#row_bottom
		{
		
		border-bottom-style:double;
		border-bottom-width:1px;
		border-bottom-color:#000;
		}
	
	.bb td, .bb th {
     	border-bottom: 1px solid black !important;
					}
	
</style>

<h3><center>Supplier Comparison Approval (Quotation Form)<center></h3>

</head>

<body>

%for o in get_object(data):
	<% setLang('en_US' or 'en_ID' ) %>
	<% seq_historical_product = 0 %>
	${o.name}
	<br />
	<table width=100% border="0" cellscpacing="0" cellpadding="0" style="font-family:arial;font-size:12px";>
	
	%for line in o.line_ids:
		<% seq_historical_product = seq_historical_product + (1 * 4)%>
		
		<tr>
			<td colspan="11">&nbsp;</td>
		</tr>
		
		<tr>
			<td >&nbsp;</td>
		    <td >Nama Produk :</td>
		    <td >PO Number :</td>
		    <td > Supplier</td>
		    <td >Qty :</td>
		    <td >Unit Price</td>
		    <td>Currency</td>
		    <td>PO Date</td>
		    <td>Delivery Time</td>
		    <td>Payment Term</td>
		    <td>Payment</td>
		</tr>
		
		<tr class="bb">
			<td colspan = "11">
			</td>
		</tr>
		
		%if get_purchase(line.product_id.id):
			<% a = get_purchase(line.product_id.id).order_id.id  or ""%>
			<tr id="row_line">
				<td>Cheapest Price</td>
			    <td>${get_purchase(line.product_id.id).name or ""}</td>
			    <td>${get_purchase_order(a).name or ""}</td>
			    <td>${get_purchase_order(a).partner_id.name or ""}</td>
			    <td>${get_purchase(line.product_id.id).product_qty or ""}</td>
			    <td>${get_purchase(line.product_id.id).price_unit or ""}</td>
			    <td>${get_purchase_order(a).pricelist_id.currency_id.name or ""}</td>
			    <td>${time.strftime('%d-%b-%Y', time.strptime( get_purchase_order(a).date_order,'%Y-%m-%d')) or ""}</td>
			    <td>${time.strftime('%d-%b-%Y', time.strptime( get_purchase_order(a).minimum_planned_date,'%Y-%m-%d')) or ""}</td>
			    <td>${get_purchase_order(a).payment_term.name or ""}</td>
			    <td>${get_purchase_order(a).journal_id.name or ""}</td>
			</tr>
			
			<% a = get_purchase2(line.product_id.id).order_id.id  or ""%>
			<tr id="row_line">
				<td>Latest Purchase</td>
			    <td>${get_purchase2(line.product_id.id).name or ""}</td>
			    <td>${get_purchase_order2(a).name or ""}</td>
			    <td>${get_purchase2(line.product_id.id).partner_id.name or ""}</td>
			    <td>${get_purchase2(line.product_id.id).product_qty or ""}</td>
			    <td>${get_purchase2(line.product_id.id).price_unit or ""}</td>
			    <td>${get_purchase_order2(a).pricelist_id.currency_id.name or ""}</td>
			    <td>${time.strftime('%d-%b-%Y', time.strptime( get_purchase_order2(a).date_order,'%Y-%m-%d')) or ""}</td>
			    <td>${time.strftime('%d-%b-%Y', time.strptime( get_purchase_order2(a).minimum_planned_date,'%Y-%m-%d')) or ""}</td>
			    <td>${get_purchase_order2(a).payment_term.name or ""}</td>
			    <td>${get_purchase_order2(a).journal_id.name or ""}</td>
			</tr>
			
			<% a = get_purchase3(line.product_id.id).order_id.id  or ""%>
			<tr id="row_line">
				<td>Six Month Purchase</td>
			    <td>${get_purchase3(line.product_id.id).name or ""}</td>
			    <td>${get_purchase_order3(a).name or ""}</td>
			    <td>${get_purchase3(line.product_id.id).partner_id.name or ""}</td>
			    <td>${get_purchase3(line.product_id.id).product_qty or ""}</td>
			    <td>${get_purchase3(line.product_id.id).price_unit or ""}</td>
			    <td>${get_purchase_order3(a).pricelist_id.currency_id.name or ""}</td>
			    <td>${time.strftime('%d-%b-%Y', time.strptime( get_purchase_order3(a).date_order,'%Y-%m-%d')) or ""}</td>
			    <td>${time.strftime('%d-%b-%Y', time.strptime( get_purchase_order3(a).minimum_planned_date,'%Y-%m-%d')) or ""}</td>
			    <td>${get_purchase_order3(a).payment_term.name or ""}</td>
			    <td>${get_purchase_order3(a).journal_id.name or ""}</td>
			</tr>
				
		%else:
			<tr id="row_line">
				<td>Cheapest Price</td>
			    <td colspan="10">Belum ada pembelian untuk barang ini</td>
			</tr>
			<tr>
				<td>Lastest Purchase</td>
				<td colspan="10">Belum ada pembelian untuk barang ini</td>
			</tr>
			<tr>
				<td>Six Month Purchase</td>
				<td colspan="10">Belum ada pembelian untuk barang ini</td>
			</tr>
		%endif
		
	%endfor
	
	</table>
	<br />
	<br />
	<br />
	
	<table width=100% border="0" cellscpacing="0" style="font-family:arial;font-size:12px";>
		<% seq_po_line = 0 %>
		%for po in get_po(o.name):
			<% seq_po_line = seq_po_line + 3 %>
			
			<tr>
				<td colspan="9">Supplier : ${po.partner_id.name}</td>
			</tr>
			<tr>
				<td colspan="9">Country : ${po.partner_address_id.country_id.name}</td>
			</tr>
			<tr bgcolor="#cccccc">
				<td></td>
				<td>Product Name</td>
				<td>Keterangan</td>
				<td>Qty</td>
				<td>UoM</td>
				<td>Price</td>
				<td>Delivery Time</td>
				<td>Payment Terms</td>
				<td>Payment</td>
			</tr>
			%for po_lines in (po.order_line):
				<% seq_po_line = seq_po_line + 1 %>
				<tr>
					<td></td>
					<td>${po_lines.product_id.name}</td>
					<td>${po_lines.ket or ""}</td>
					<td>${po_lines.product_qty}</td>
					<td>${po_lines.product_uom.name}</td>
					<td>${formatLang(float(po_lines.price_unit),digits=get_digits(dp='Purchase Price'))}  ( ${po.pricelist_id.currency_id.name} )</td>
					<td>${time.strftime('%d-%b-%Y', time.strptime( po_lines.date_planned,'%Y-%m-%d')) or ""}</td>
					<td>${po.payment_term.name}</td>
					<td>${po.journal_id.name}</td>
				</tr>   
			%endfor
				<tr bgcolor="black">
					<td colspan="9"></td>
				</tr>
				<tr height:10mm>
					<td colspan="9"><div class="wrap">&nbsp;</div></td>
				</tr>		
		%endfor
		
	</table>
	
	<!-- <p style="page-break-after:always"></p> -->
	<table border="0" cellscpacing="0" cellpadding="0" align="right">
	
	<% 
	total_line =  seq_historical_product + seq_po_line
	if total_line <= 20:
		add_line = 0
	else:
		add_line = 30 - total_line  
		if add_line <= 0:
			add_line = 0
	
	%>
	%for add_linex in range (add_line):
		<tr>
			<td>&nbsp;</td>
		</tr>
	%endfor
	
	%for po in get_po_approve(o.name):
		<tr>
			<td>Recommended Supplier :</td>
			<td colspan="2"><b>${po.partner_id.name}</b></td>
			<td colspan="3"><b>${po.name}</b></td>
		</tr>
		<tr id="row_head_line">
			<td class="head_left_sign"></td>
			<td class="head_sign" width=150>CEO</td>
			<td class="head_sign" width=150>Project Director</td>
			<td class="head_sign" width=150>HR Director</td>
			<td class="head_sign" width=150>Procurement Manager</td>
			<td class="head_sign" width=150>Procurement Staff(Buyer)</td>
		</tr>
		<tr>
			<td class="head_left_sign"></td>
			<td class="wrap2"></td>
			<td class="wrap2"></td>
			<td class="wrap2"></td>
			<td class="wrap2"></td>
			<td class="wrap2"></td>
		</tr>
		<tr>
			<td class="head_left_sign"></td>
			<td class="bottom_sign"><center>Soebianto</center></td>
			<td class="bottom_sign"><center>Veera</center></td>
			<td class="bottom_sign"><center>(__________________)</center></td>
			<td class="bottom_sign">(__________________)</td>
			<td class="bottom_sign">(__________________)</td>
		</tr>
	
	%endfor
	</table>
	
	
%endfor
</body>
</html>



			    	