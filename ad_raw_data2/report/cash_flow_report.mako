<html>
<body>

<table width="100%" height="100%">
	<tr>
		<td>Nama</td>
		<td>Keterangan</td>
		<td>Cash Flow Account</td>
	</tr>
	<% 
		no 		= 0 
		amount	= 0.0
	%>
	%for i in get_move_line(data):
		<% no += 1%>
		
		%if i.debit <> 0.0:
			<%amount = i.debit %>
		%else:
			<% amount = i.debit - i.credit %>
		%endif
		
		
		%if i.account_id.cash_flow_categ == 'cfo_customer':
			<tr>
				<td>${i.move_id.partner_id.name}</td>
				<td>${i.name}</td>
				<td>${i.account_id.cash_flow_categ}</td>
			</tr>
		%elif i.account_id.cash_flow_categ == 'cfo_supplier':
			<tr>
				<td>${i.move_id.partner_id.name}</td>
				<td>${i.name}</td>
				<td>${i.account_id.cash_flow_categ}</td>
			</tr>
		
		%elif i.account_id.cash_flow_categ == 'cfo_interest_expense':
			<tr>
				<td>${i.move_id.partner_id.name}</td>
				<td>${i.name}</td>
				<td>${i.account_id.cash_flow_categ}</td>
			</tr>
		%elif i.account_id.cash_flow_categ == 'cfo_income_tax':
			<tr>
				<td>${i.move_id.partner_id.name}</td>
				<td>${i.name}</td>
				<td>${i.account_id.cash_flow_categ}</td>
			</tr>
		%elif i.account_id.cash_flow_categ == 'cfo_due_from_related_parties':
			<tr>
				<td>${i.move_id.partner_id.name}</td>
				<td>${i.name}</td>
				<td>${i.account_id.cash_flow_categ}</td>
			</tr>
		%elif i.account_id.cash_flow_categ == 'cfo_other':
			<tr>
				<td>${i.move_id.partner_id.name}</td>
				<td>${i.name}</td>
				<td>${i.account_id.cash_flow_categ}</td>
			</tr>
		%endif
	%endfor
	
</table>
</body>
</html>