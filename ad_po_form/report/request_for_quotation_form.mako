<html>

<head>
<title>REQUEST FOR QUOTATION</title>
<style>
	
	.wrap
		{
		height:0mm
		}
	
	.row_col
		{
		padding:5px;
		border-top-style:double;
		border-top-width:1px;
		border-top-color:#000;
		border-bottom-style:double;
		border-bottom-width:1px;
		border-bottom-color:#000;
		border-left-style:solid;
		border-left-width:1px;
		border-left-color:#000;
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		
		}
		
	.row_col_left
		{
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		}
		
	row_col_right
		{
		border-left-style:solid;
		border-left-width:1px;
		border-left-color:#000;
		}
		
	#row_head
		{
		border-top-style:double;
		border-bottom-style:double;
		}
	
	.row_line
		{
		padding:5px;
		
		border-left-style:solid;
		border-left-width:1px;
		border-left-color:#000;
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		}
		
	.row_line_left
		{
		padding:5px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		}
		
	.row_line_right
		{
		padding:5px;
		
		border-left-style:solid;
		border-left-width:1px;
		border-left-color:#000;
		vertical-align:top;
		}
	
	#row_head_line
		{
		font-size:12px;
		border-top-style:none;
		border-bottom-none;
		}
		
	#row_head_sub_line
		{
		font-size:14px;
		border-top-style:solid;
		
		}
	
	#row_head_sub_terbilang
		{
		font-size:14px;
		
		}
		
	.sub_line
		{
		padding:5px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		
		}
	
</style>
</head>

<body>
<div style="border: 2px black groove; text-align: left; width=100%">



%for o in get_object(data):
	<h2><u><center>PT. GUNUNG BARA UTAMA</center></u></h2>
	<h3><center>No. ${o.rfq_number}</center></h3>
	<br>&nbsp;
	</center>
	<!--
	
	-->
	<% setLang('en_US' or 'en_ID' ) %>


<table width=100% border="0" cellscpacing="0" style="font-family:arial;font-size:12px";>
  <tr>
  	<td colspan=2 valign="top" width="50%">
  		<table border="0" cellscpacing="0" style="font-family:arial;font-size:12px">
	  		<tr>
	  			<td colspan=2><strong>${o.partner_id.name  or " "}</strong></td>
	  		</tr>
	  		<tr>
	  			<td colspan=2><strong>${o.partner_address_id.name  or " "}</strong></td>
	  		</tr>
	  		<tr>
	  			<td colspan=2>${o.partner_address_id.street  or " "}</td>
	  		</tr>
	  		<tr>
	  			<td colspan=2>${o.partner_address_id.city  or " "}</td>
	  		</tr>
	  		<tr>
	  			<td colspan=2>${o.partner_address_id.country_id.name  or " "}</td>
	  		</tr>
	  		<tr>
	  			<td>Phone</td>
	  			<td>: ${o.partner_address_id.fax  or " "}</td>
	  		</tr>
	  		<tr>
	  			<td>Fax</td>
	  			<td>: ${o.partner_address_id.fax  or " "}</td>
	  		</tr>
	  		<tr>
	  			<td>Email</td>
	  			<td>: ${o.partner_address_id.email  or " "}</td>
	  		</tr>
  		</table>
  	</td>
  	<td colspan=2 width="50%">
  		<table border="0" cellscpacing="0" style="font-family:arial;font-size:12px">
  			<tr>
  				<td>PR No.</td>
  				<td>: ${o.requisition_id.name  or " "}</td>
  			</tr>
  			<tr>
  				<td>Quotation Submission Deadline</td>
  				<td>: ${time.strftime('%d-%b-%Y', time.strptime( o.date_order,'%Y-%m-%d')) or ""}</td>
  			</tr>
  			<tr>
  				<td>Request Data End User</td>
  			</tr>
  			<tr>
  				<td>Shipping Date</td>
  				<td>: ${time.strftime('%d-%b-%Y', time.strptime( o.minimum_planned_date,'%Y-%m-%d')) or ""}</td>
  			</tr>
  			<tr>
  				<td>Contact Person</td>
  				<td>: ${o.delegate.name or ""}</td>
  			</tr>
  			<tr>
  				<td>E-mail</td>
  				<td>: ${o.delegate.user_email or ""}</td>
  			</tr>
  			<tr>
  				<td>&nbsp;</td>
  				<td>Currency ( ${o.pricelist_id.currency_id.name} )</td>
  			</tr>
  		</table>
  	</td>
  </tr>
  
  </table>
  
  <table width=100% cellscpacing="0" style="border-collapse:collapse;font-family:arial;font-size:12px";>
  <tr id="row_head" style="font-family:arial;font-size:14px" bgcolor = "bfbfbf";>
    <th class="row_col_left" rowspan="2" width="5%" >No</th>
    <th class="row_col" colspan="2" width="40%"  rowspan="2">ITEM</th>
    <th class="row_col" rowspan="2" width="30%" >DESCRIPTION</th>
    <th class="row_col" colspan="4">UNIT</th>
  </tr>
  
  <tr id="row_head" bgcolor="bfbfbf">
    <th class="row_col" colspan="3" width="8%" >Quantity</th>
    <th class="row_col" colspan="2" width="8%" >UOM</th>
  </tr>
  
  %for o in get_object(data):
	  <%a=1%>
	  %for order_line in [line for line in o.order_line]:
		  <tr id="row_head_line">
		    
		    <td class="row_line_left" style="text-align: center" ><div class="wrap">${a}</div></td>
		    <td class="row_line" colspan="2">[${order_line.product_id.code}]${order_line.product_id.name}</td>
		    <td class="row_line">${order_line.ket or ""}</td>
		    <td class="row_line" colspan="3" style="text-align: center">${order_line.product_qty}</td>
		    <td class="row_line" colspan="2" style="text-align: center" >${order_line.product_uom.name}</td>
		    
		  </tr>
	  	<%a+=1%>
	  %endfor
  %endfor
  
  ${blank_line_rfq([line for line in o.order_line])}
  
  <tr bgcolor="bfbfbf">
    <td class="sub_line" style="text-align: center;padding-top:10px" colspan="3"><strong>Shipping Address :<br />&nbsp;</strong> </td>
    <td class="sub_line" style="text-align: center;padding-top:10px" colspan="5"><strong>Invoice Address :<br />&nbsp;</strong> </td>
  </tr>
  
  <tr id="row_head_sub_line">
    <td class="sub_line" colspan="3" style="vertical-align:top;padding:10px">
    	<strong>${o.dest_material_addrs.name or ""}<br />
    	${o.dest_material_addrs.partner_id.name or ""}</strong><br />
	 	${o.dest_material_addrs.street or ""}<br />
	 	${o.dest_material_addrs.city or ""}<br />
		${o.dest_material_addrs.phone or ""}<br />&nbsp;</td>
    <td class="sub_line" colspan="5" style="vertical-align:top;padding:10px">
    	<strong>${get_company_address(o.company_id).name or ""}<br />
    	${o.company_id.name or ""}<br /></strong> 
    	${get_company_address(o.company_id).street or ""}<br /> 
    	${get_company_address(o.company_id).street2 or ""}<br /> 
    	${get_company_address(o.company_id).phone or ""}; ${get_company_address(o.company_id).fax or ""}</td>
  </tr>
</table>
%endfor
</div>
</body>
</html>