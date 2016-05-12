<html>

<body>

<div style="border: 2px black groove; padding: 5px; text-align: left; width=90%">
%for o in get_object(data):
	<h2><u><center>PT. GUNUNG BARA UTAMA</u>
	<br>( WORK ORDER )
	<br>${o.name}
	</center></h2>
	
	<% 
	setLang(o.partner_id.lang) 
	print "o.partner_id.lang",o.partner_id.lang
	%>

	<table border="0" width="100%">
		<tr>
			<td colspan="2" width="50%">KEPADA YTH.</td>
			<td>MPB No</td>
			<td>: ${o.requisition_id.name  or " "}</td>
		</tr>
		<tr>
			<td colspan="2"><b>${o.partner_id.name  or " "}</b></td>
			<td>Tgl PO</td>
			<td>: ${time.strftime('%d-%b-%Y', time.strptime( o.date_order,'%Y-%m-%d')) or ""}</td>
		</tr>
		<tr>
			<td colspan="2">${o.partner_address_id.street  or " "}</td>
			<td>Cara Pembayaran</td>
			<td></td>
		</tr>
		<tr>
			<td colspan="2">${o.partner_address_id.city  or " "}</td>
			<td>Masa Pembayaran</td>
			<td>: ${o.payment_term.name  or " "}</td>
		</tr>
		<tr>
			<td colspan="2">${o.partner_address_id.country_id.name  or " "}</td>
			<td>Tgl Pengiriman</td>
			<td>: ${time.strftime('%d-%b-%Y', time.strptime( o.minimum_planned_date,'%Y-%m-%d')) or ""}</td>
		</tr>
		<tr>
			<td>Phone</td>
			<td>: ${o.partner_address_id.phone  or " "}</td>
			<td>Contact Person</td>
			<td>: </td>
		</tr>
		<tr>
			<td>Fax</td>
			<td>: ${o.partner_address_id.fax  or " "}</td>
			<td>Email</td>
			<td>: </td>
		</tr>
		<tr>
			<td>Email</td>
			<td><u>${o.partner_address_id.email  or " "}</u></td>
			<td></td>
			<td></td>
		</tr>
		<tr>
			<td>Attn</td>
			<td><b>${o.partner_address_id.name  or " "}</b></td>
			<td></td>
			<td></td>
		</tr>
		<tr>
			<td></td>
			<td>${o.partner_address_id.mobile  or " "}</td>
			<td></td>
			<td></td>
		</tr>
	</table>

	%for po_lines in o.order_line:
	
		${po_lines.name}
		
	%endfor
	
%endfor
</div>

</body>
</html>