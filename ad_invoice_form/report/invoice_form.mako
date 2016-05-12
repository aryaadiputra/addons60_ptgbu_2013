<html>
<head>
<style>

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
		
.sub_line
		{
		background:gray;
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		border-top-width:1px;
		border-top-style:double;
		border-bottom-style:double;
		}


#row_head
		{
		border-top-style:solid;
		}

#sign
		{
		border-top-style:solid;
		}
#sign_end
		{
		border-bottom-style:solid;
		}

.sign_mid
		{
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		border-top-width:1px;
		border-top-style:solid;
		border-bottom-style:solid;
		border-left-width:1px;
		border-left-style:solid;
		}

.sign_right
		{
		border-right-style:solid;
		border-right-width:1px;
		border-right-color:#000;
		
		border-left-style:solid;
		border-left-width:1px;
		border-left-color:#000;
		}
.sign_left
		{
		border-left-style:solid;
		border-left-width:1px;
		border-left-color:#000;
		}
	

</style>
</head>
<body>
<% setLang('en_US' or 'en_ID' ) %>
%for o in get_object(data):
	<table width=100% border="0" cellscpacing="0" style="font-family:arial;font-size:11px"; border-collapse:"collapse";>
	<tr>
		<td colspan = 3>${helper.embed_image("jpg",o.company_id.logo, )}<img src="" alt="" >		</td>
		<td colspan = 5><center><strong>PAYMENT APLICATION</strong></center></td>
		<td>Print Date</td>
		<td>: ${get_process_date()}</td>
	</tr>
	<tr>
		<td colspan = 3></td>
		<td colspan = 5><center><strong>(SUPPLIER INVOICE)</strong></center></td>
		<td>Page</td>
		<td>: </td>
	</tr>
	<tr>
		<td>SI No.</td>
		<td colspan = 7>: ${o.number}</td>
		<td>Invoice Date</td>
		<td>: ${o.date_invoice_out or ""}</td>
	</tr>
	<tr>
		<td>Supplier</td>
		<td colspan = 7>: ${o.partner_id.name}</td>
		<td>Receive Date</td>
		<td>: ${o.date_invoice or ""}</td>
	<tr/>
	<tr>
		<td>Address</td>
		<td colspan = 7>: ${o.address_invoice_id.street or "/"}, ${o.address_invoice_id.street2 or ""}</td>
		<td>Due Date</td>
		<td>: ${o.date_due or ""}</td>
	<tr/>
	<tr>
		<td>N.P.W.P</td>
		<td colspan = 7>: </td>
		<td></td>
		<td></td>
	<tr/>
	<tr>
		<td>Origin Doc</td>
		<td colspan = 7>: ${o.origin or ""}</td>
		<td></td>
		<td></td>
	<tr/>
	<tr>
		<td>Description</td>
		<td colspan = 7>: ${o.name or ""}</td>
		<td></td>
		<td></td>
	<tr/>
	
	<tr>
		<td colspan=9></td>
		<td><i>Currency : ${o.currency_id.name}</i></td>
	</tr>
	
	<tr >
		<td class="sub_line">No.</td>
		<td class="sub_line">Account</td>
		<td class="sub_line">Item</td>
		<td class="sub_line">Item name</td>
		<td class="sub_line">Qty</td>
		<td class="sub_line">UoM</td>
		<td class="sub_line">Unit Price</td>
		<td class="sub_line">Disc</td>
		<td class="sub_line">Amount</td>
		<td class="sub_line">Budget Remain</td>
	</tr>
	
	<%no=0%>
	%for line in o.invoice_line:
		<%no += 1%>
		<tr>
			<td>${no}</td>
			<td>${line.account_id.code}</td>
			<td>${line.product_id.default_code or ""}</td>
			<td>${line.product_id.name or "" or line.name}</td>
			<td>${line.quantity}</td>
			<td>${line.uos_id.name or ""}</td>
			<td>${formatLang(int(line.price_unit),digits=get_digits(dp='Purchase Price'))}</td>
			<td>${line.discount}%</td>
			<td>${formatLang(int(line.price_subtotal),digits=get_digits(dp='Purchase Price'))}</td>
			<td>${formatLang(int(amount_remain(line.account_analytic_id.id, line.invoice_id.id, line.invoice_id.date_invoice[:4])),digits=get_digits(dp='Purchase Price'))}</td>
		</tr>
	
	%endfor
	<tr>
		<td colspan=10>&nbsp;</td>
	</tr>
	<tr>
		<td colspan=10>&nbsp;</td>
	</tr>
	<tr>
		<td colspan=10><strong><u>Tax Information</strong></></td>
	</tr>
	
	%for tax_line in o.tax_line:
		<tr>
			<td colspan=2>${tax_line.name}</td>
			<td >${formatLang(int(tax_line.tax_amount),digits=get_digits(dp='Purchase Price'))}</td>
			<td colspan=7></td>
		</tr>
	%endfor
	<tr style="font-weight:bold; text-align: right";>
		<td colspan=6></td>
		<td>Net Total :</td>
		<td></td>
		<td>${formatLang(int(o.amount_untaxed),digits=get_digits(dp='Purchase Price'))}</td>
		<td></td>
	</tr>
	<tr style="font-weight:bold; text-align: right";>
		<td colspan=6></td>
		<td>Disc :</td>
		<td></td>
		<td></td>
		<td></td>
	</tr>
	<tr style="font-weight:bold; text-align: right";>
		<td colspan=6></td>
		<td >Taxes :</td>
		<td></td>
		<td>${formatLang(int((o.amount_ppn - o.holding_taxes) or 0.0),digits=get_digits(dp='Purchase Price'))}</td>
		<td></td>
	</tr>
	<tr style="font-weight:bold; text-align: right";>
		<td colspan=6></td>
		<td >TOTAL :</td>
		<td></td>
		<td>${formatLang(int(o.to_be_paid),digits=get_digits(dp='Purchase Price'))}	${}</td>
		<td></td>
	</tr>
	</table>
	
	
	<br />
	<br />
	<table width=100% cellscpacing="0" style="border-collapse:collapse;font-family:arial;font-size:11px";>
	<tr>
		<td><strong>Payment Method : <strong><strong></td>
		<td><strong>&nbsp;<input type="checkbox" ${compute_lines(o.id, 'cash')}> Cash <strong></td>
		<td><strong>&nbsp;<input type="checkbox" ${compute_lines(o.id, 'cheque')}> Giro : ______________<strong></td>
		<td><strong>&nbsp;<input type="checkbox" ${compute_lines(o.id, 'transfer')}> Transfer <strong></td>
		<td><strong>&nbsp;<input type="checkbox" ${compute_lines(o.id, 'free_transfer')}> Others : ______________<strong></td>
	</tr>
	</table>
	
	<br />
	<br />
	<table width=100% cellscpacing="0" style="border-collapse:collapse;font-family:arial;font-size:12px";>
	<tr id="row_head">
		<td class="sign_right">Cost Control :</td>
		<td class="sign_right">Treasury :</td>
		<td class="sign_right" colspan=2 >Approved By :</td>
		<td class="sign_right">Received By  :</td>
	</tr>
	<tr>
		<th class="sign_right"></th>
		<th class="sign_right"></th>
		<th class="sign_mid">GM Finance :</th>
		<th class="sign_mid">GM/Director/CEO</th>
		<th class="sign_right"></th>
	</tr>
	<tr id="row_head">
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
	</tr>
	<tr>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
	</tr>
	<tr>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
	</tr>
	<tr id = "sign_end">
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
		<td class="sign_right">&nbsp;</td>
	</tr>
	</table>
%endfor
</body>
</html>