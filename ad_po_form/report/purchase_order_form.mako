<html>

<head>
<title>WORK ORDER</title>
<style>

	.border_left
	{
	border-left: solid black 1px
	}

	#watermark {
	  color: #d0d0d0;
	  font-size: 120pt;
	  -webkit-transform: rotate(-45deg);
	  -moz-transform: rotate(-45deg);
	  position: fixed;
	  width: 100%;
	  height: 100%;
	  margin: 0;
	  z-index: -1;
	  left:350px;
	  top:350px;
	}
	.center
	{
	text-align:center;
	}
	
	.border_top
	{
	border-top:solid 1px black
	}
		
	.ttd
	{
	text-align:center;
	padding-bottom:80px;
	width:50%
	}

	.nama
	{
	text-align:center;
	width:50%;
	font-weight:bold;
	}
	
	.padding
	{
		padding-right:100px;
	}
		
	.copy
	{
		text-align:right;
		font-size:18px;
	}
	
	.wrap
		{
		height:0mm
		}
	
	.row_col
		{
		padding:1px;
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
		padding:1px;
		
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
		padding:1px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		vertical-align:top;
		}
		
	.row_line_right
		{
		padding:1px;
		
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
		
	#row_head_alamat
		{
		font-size:14px;
		
		}
	
	#row_head_sub_terbilang
		{
		font-size:14px;
		
		}
	
	.calc
	{
	padding:3px;
	border:solid black 1px;
	}
		
	.sub_line
		{
		padding:15px;
		
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		border-top-style:solid;
		border-top-width:1px;
		border-top-color:#000;
		
		}
</style>
</head>

<body>

%for o in get_object(data):
	%if o.print_seq<>1:
		<div id="watermark">
			COPY: ${o.print_seq}
		</div>
	%endif
<div style="border: 2px black groove; text-align: left; width=100% height=100%">
	<h2><u><center>PT. GUNUNG BARA UTAMA</u>
	<br>( WORK ORDER )
	<br>No. ${o.name}</h2>
	</center>
	<!--
	
	-->
	<% setLang('en_US' or 'en_ID' ) %>


<table width=100% border="0" cellscpacing="0" style="font-family:arial;font-size:12px";>
  <tr>
  	<td colspan=2 valign="top" width="65%">
  		<table border="0" cellscpacing="0" style="font-family:arial;font-size:12px">
	  		<tr>
	  			<td colspan=2><strong>${o.partner_id.name  or " "}</strong></td>
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
	  		<tr>
	  			<td>Contact Person</td>
	  			<td>: <strong>${o.partner_address_id.name  or " "}</strong></td>
	  		</tr>
  		</table>
  	</td>
  	<td colspan=2 width="35%">
  		<table border="0" cellscpacing="0" style="font-family:arial;font-size:12px">
  			<tr>
  				<td>PO No.</td>
  				<td>: ${o.requisition_id.name  or " "}</td>
  			</tr>
  			<tr>
  				<td>Date</td>
  				<td>: ${time.strftime('%d-%b-%Y', time.strptime( o.date_order,'%Y-%m-%d')) or ""}</td>
  			</tr>
  			<tr>
  				<td>Payment Method</td>
  				<td>: ${o.journal_id.name  or " "}</td>
  			</tr>
  			<tr>
  				<td>Payment Term</td>
  				<td>: ${o.payment_term.name  or " "}</td>
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
  				<td>( ${o.pricelist_id.currency_id.name} )</td>
  			</tr>
  		</table>
  	</td>
  </tr>
</table>
  
<table width=100% cellscpacing="0" style="border-collapse:collapse;font-family:arial;font-size:12px";>
  <tr id="row_head" style="font-family:arial;font-size:14px";>
    <th class="row_col_left" width="5%" rowspan="2">No</th>
    <th class="row_col" colspan="2" rowspan="2">ITEM</th>
    <th class="row_col" colspan="2">UNIT</th>
    <th class="row_col" width=15% rowspan="2">UNIT PRICE</th>
    <th class="row_col_right"  width=10% rowspan="2">SUB TOTAL</th>
  </tr>
  <tr id="row_head">
    <th class="row_col" width="8%" >Quantity</th>
    <th class="row_col" width="8%" >UOM</th>
  </tr>
 
  <!-- %for o in get_object(data): -->
	  <%a=1%>
	  %for line in o.order_line:
		  <tr id="row_head_line">
		    
		    <td class="row_line_left" style="text-align: center" ><div class="wrap">${a}</div></td>
		    <td class="row_line" colspan="2">${line.product_id.name} 
		    %if line.ket:
		    	<br />
		    	(${line.ket or ""})
		    %endif
		    </td>
		    
		    <td class="row_line" style="text-align: center">${line.product_qty}</td>
		    <td class="row_line" style="text-align: center" >${line.product_uom.name}</td>
		    <td class="row_line" style="text-align: right" >${formatLang(int(line.price_unit),digits=get_digits(dp='Purchase Price'))}</td>
		    <td class="row_line_right" style="text-align: right" >${formatLang(int(line.price_subtotal),digits=get_digits(dp='Purchase Price'))}</td>
		    
		  </tr>
	  	<%a+=1%>
	  <!-- %endfor -->
  %endfor
  ${blank_line([line for line in o.order_line])}
  
  <tr>
    <td class="calc" colspan="5" rowspan="4">
    	<strong>Amount: <br /><br />
    	<i> ${o.pricelist_id.currency_id.name} # ${ convert(get_grand_total(o.amount_total,o.landed_cost_line),o.pricelist_id.currency_id.name) } #
    	</strong>
    </td>
    <td class="calc"><strong>TOTAL</strong></td>
    <td class="calc" style="text-align: right">${formatLang(int(o.amount_untaxed),digits=get_digits(dp='Purchase Price'))}</td>
  </tr>
  
  <tr id="row_head_sub_terbilang">
    <td class="calc" ><strong>PPN 10% </strong></td>
    <td class="calc" style="text-align: right" >${formatLang(int(o.amount_tax),digits=get_digits(dp='Purchase Price'))}</td>
  </tr>
  <tr id="row_head_sub_line">
    <td class="calc" ><strong>Charge</strong> </td>
    <td class="calc" style="text-align: right">${formatLang(int(charge(o.landed_cost_line)),digits=get_digits(dp='Purchase Price'))}</td>
  </tr>
  <tr id="row_head_sub_line">
    <td class="calc" ><strong>GRAND TOTAL</strong> </td>
    <td style="text-align: right">${formatLang(int(o.amount_total)+int(charge(o.landed_cost_line)),digits=get_digits(dp='Purchase Price'))}</td>
  </tr>
  
  
  <tr id="row_head_sub_line">
  	<td colspan=7 class="sub_line">
  		<table width="100%" style="border-collapse:collapse;font-family:arial;font-size:12px">
  			<tr>
  				<td width="65%">
  					<strong>Shipping Address:<br /><br />
					${o.dest_material_addrs.name or ""}<br />
					${o.dest_material_addrs.partner_id.name or ""}</strong><br />
					${o.dest_material_addrs.street or ""}<br />
					${o.dest_material_addrs.city or ""}<br />
					${o.dest_material_addrs.phone or ""}<br />
  				</td>
  				<td width="35%">
  					<strong>Invoice Address:<br /><br />
					${get_company_address(o.company_id).name or ""}<br /> 
					${o.company_id.name or ""} </strong><br /> 
					${get_company_address(o.company_id).street or ""}<br /> 
					${get_company_address(o.company_id).street2 or ""}<br /> 
					${get_company_address(o.company_id).phone or ""};
 					${get_company_address(o.company_id).fax or ""}  					
  				</td>
  			</tr>
  		</table>
  </tr>
  <tr id="row_head_sub_line">
  	<td colspan=7 class="sub_line">
  		<table width="100%">
  			<tr>
  				<td class="ttd">Approved by Supplier</td>
  				<td class="ttd">Your Signature</td>
  			</tr>
  			<tr>
  				<td class="center">(_____________________)</td>
  				<td class="center">(_____________________)</td>
  			</tr>
  			<tr>
  				<td class="nama">Sign &amp; Clear Name</td>
  				<td class="nama">Sign &amp; Clear Name</td>
  			</tr>
  		</table>
  	</td>
  </tr>
</table>
%endfor
</div>
</body>
</html>