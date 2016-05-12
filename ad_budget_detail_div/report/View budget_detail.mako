<html>
<head>
<style>
table
	{
	font-size:10px;
	}
#header2 th
	{
	border-bottom:1px solid #000;
	border-top:1px solid #000;
	}
.total1 td
	{
	border-top:1px dashed #000;
	}
.total2 td
	{
	border-top:1px solid #000;
	}
.subhead td
	{
	border-bottom:1px solid #D1D1D1;
	}
	
.head_table
	{
	color:white;
	background-color:grey;
	}
	
.line_table
	{
	font-weight:bold;
	}

.row_col_actual
	{
	border-bottom-style:solid;
	border-bottom-width:1px;
	border-bottom-color:#000;
	}
.line
	{
	border-bottom-style:solid;
	border-bottom-width:1px;
	border-bottom-color:#000;
	}
	
.header_total
	{
	border-top-style:solid;
	border-top-width:1px;
	border-top-color:#000;
	
	border-left-style:solid;
	border-left-width:1px;
	border-left-color:#000;
	
	border-right-style:solid;
	border-right-width:1px;
	border-right-color:#000;
	cellspacing="0";
	border-collapse:collapse;
	}
	
.body_total
	{
	border-left-style:solid;
	border-left-width:1px;
	border-left-color:#000;
	
	border-right-style:solid;
	border-right-width:1px;
	border-right-color:#000;
	cellspacing="0";
	border-collapse:collapse;
	}

.break
	{
	page-break-after:always;
	}
</style>
</head>
<body>
	
	<% setLang(company.partner_id.lang) %>
	<br/>
	<br/>
	
	<table width="100% cellpadding="3">
		<tr>
			<td align="left" style="font-size:8px;">${ time.strftime("%r") },  ${ time.strftime("%B %d, %Y") }</td>
		</tr>
	</table>
	<br/>
	<br/>
	<table width="100% cellpadding="3">
		<tr>
			<th align="left" style="font-size:14px;">${ company.partner_id.name }</th>
		</tr>
		<tr>
			<th align="left" style="font-size:10px;">Detail of Account :</th>
		</tr>
		%for i in get_budget_item(data):
			<tr>
				<th align="left" style="font-size:10px;">${i.name}</th>
			</tr>
		%endfor
		
			<tr>
				<th align="left" style="font-size:10px;"><i>As of </i>${get_as_of_date(data)}</th>
			</tr>
		
	</table>
	%if len(get_department(data))>0: 
		%for d in get_department(data):
			<table width="100% cellpadding="3" class="break">
				<!-- <tr>
					<td colspan="14"><h2>${d.name}</h2></td>
				</tr> -->
				<tr class ="head_table">
					<td align="center" style="font-size:14px;">No.</td>
					<td align="center" style="font-size:14px;">Account</td>
					<td align="center" style="font-size:14px;">Description</td>
					<td align="center" style="font-size:14px;"><i>${data['form']['1']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['2']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['3']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['4']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['5']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['6']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['7']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['8']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['9']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['10']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['11']['date']}</i></td>
					<td align="center" style="font-size:14px;"><i>${data['form']['12']['date']}</i></td>
					<td class="header_total" =align="center" style="font-size:14px;">TOTAL</td>
					<!-- <td align="center" style="font-size:14px;">TOTAL BUDGET</td> -->
					<!-- <td align="center" style="font-size:14px;">REMAINING BUDGET</td> -->
				</tr>
				<%number=0%>
				<%subnumber=0%>
				%for i in get_data(data):
					
					%if data['form']['without_zero']:
						%if i['balance']:
							%if i['type'] == 'view':
								<%number+=1%>
								<%subnumber=0%>
								<%no = number%>
								<%subno = ''%>
								<% bold = 'class="line_table"' %>
							%else:
								<%subnumber+=1%>
								<%subno = str(number)+'.'+str(subnumber)%>
								<%no = ''%>
								<% bold = '' %>
							%endif	
							<tr ${bold}>
								
								<td align="center" style="font-size:14px;">${no}</td>
								<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;"></span><span style="font-size:8px;">${subno}      ${ i['name'] }</span></td>
								<td align="right" style="font-size:10px;">Budget :</td>								
								<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<!--*****-->
								<%total_budget = get_period_budget_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'], d['id'])%>
								<td class="body_total" align="center" style="font-size:10px;"> ${ formatLang(total_budget,digits=get_digits(dp='Budget')) or 0.0}</td>
								<!-- <td align="center" style="font-size:10px;">${ formatLang(total_budget,digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
							<!-- ########################Actual######################## -->
							<tr ${bold}>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" style="font-size:10px;"></td>
								<td align="right" style="font-size:10px;">Actual :</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;"> ${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<!--*****-->
								<%total_actual = get_period_actual_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'], d['id'])%>
								<td class="body_total" align="center" style="font-size:10px;"> ${ formatLang(total_actual,digits=get_digits(dp='Budget')) or 0.0}</td>
								<!-- <td align="center" style="font-size:10px;">${ formatLang(total_actual,digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
							<!-- ###################################################### -->
							<!-- ########################Under/ Over######################## -->
							<tr ${bold}>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" style="font-size:10px;"></td>
								<td align="right" style="font-size:10px;">Under/ Over :</td>
								<td align="right" style="font-size:10px;">  ${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class="body_total" align="center" style="font-size:10px;"> ${ formatLang((total_budget-total_actual),digits=get_digits(dp='Budget')) or 0.0} </td>
								<!-- <td align="center" style="font-size:10px;">${ formatLang((total_budget-total_actual),digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
							<!-- ###################################################### -->
							<tr>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" colspan="14"><u>Actual</u></td>
								<td class="body_total" align="center" style="font-size:14px;"></td>
							</tr>
							
							<!-- ########################Actual Transaction######################## -->
							%if data['form']['with_transaction'] and i['type'] == 'normal':
								%for t in get_transaction(data['form']['as_of_date'],i['id'], d['id']):
									<tr ${bold}>
										<td align="center" style="font-size:14px;"></td>
										<td align="left" style="font-size:10px;">- ${t.name}</td>
										<td align="right" style="font-size:10px;"></td>
										
										<!--*****************-->
										<% actual_1 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['1']['start'], data['form']['1']['end'], t['id'], d['id']) %>
										<% actual_2 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['2']['start'], data['form']['2']['end'], t['id'], d['id']) %>
										<% actual_3 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['3']['start'], data['form']['3']['end'], t['id'], d['id']) %>
										<% actual_4 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['4']['start'], data['form']['4']['end'], t['id'], d['id']) %>
										<% actual_5 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['5']['start'], data['form']['5']['end'], t['id'], d['id']) %>
										<% actual_6 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['6']['start'], data['form']['6']['end'], t['id'], d['id']) %>
										<% actual_7 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['7']['start'], data['form']['7']['end'], t['id'], d['id']) %>
										<% actual_8 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['8']['start'], data['form']['8']['end'], t['id'], d['id']) %>
										<% actual_9 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['9']['start'], data['form']['9']['end'], t['id'], d['id']) %>
										<% actual_10 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['10']['start'], data['form']['10']['end'], t['id'], d['id']) %>
										<% actual_11 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['11']['start'], data['form']['11']['end'], t['id'], d['id']) %>
										<% actual_12 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['12']['start'], data['form']['12']['end'], t['id'], d['id']) %>
										
										<!--*****************-->
										<td align="right" style="font-size:10px;">  ${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['1']['start'], data['form']['1']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['2']['start'], data['form']['2']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['3']['start'], data['form']['3']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['4']['start'], data['form']['4']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['5']['start'], data['form']['5']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['6']['start'], data['form']['6']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['7']['start'], data['form']['7']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['8']['start'], data['form']['8']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['9']['start'], data['form']['9']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['10']['start'], data['form']['10']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['11']['start'], data['form']['11']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['12']['start'], data['form']['12']['end'], t['id'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
									
										<!-- <td align="center" style="font-size:14px;"> ${ formatLang(get_period_actual_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'], d['id']),digits=get_digits(dp='Budget')) or 0.0 }</td> -->
										<td class="body_total" align="center" style="font-size:10px;"> ${ actual_1 + actual_2 + actual_3 + actual_4 + actual_5 + actual_6 + actual_7 + actual_8 + actual_9 + actual_10 + actual_11 + actual_12 } </td>
										<!-- <td align="center" style="font-size:10px;">${ actual_1 + actual_2 + actual_3 + actual_4 + actual_5 + actual_6 + actual_7 + actual_8 + actual_9 + actual_10 + actual_11 + actual_12 }</td> -->
										<!-- <td align="center" style="font-size:11px;"></td> -->
									</tr>
								%endfor
							%endif
							<tr>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" colspan="14"><u>Budget (unutilized)</u></td>
								<td class="body_total" align="center" style="font-size:14px;"></td>
							</tr>
							
							<tr ${bold}>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" style="font-size:10px;">- ${ get_desc_budget_line(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], d['id'])}</td>
								<td align="right" style="font-size:10px;"></td>
								
								<!--********************-->
								<%unutulized_1 = get_period_unutilized(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_2 = get_period_unutilized(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_3 = get_period_unutilized(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_4 = get_period_unutilized(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_5 = get_period_unutilized(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_6 = get_period_unutilized(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_7 = get_period_unutilized(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_8 = get_period_unutilized(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_9 = get_period_unutilized(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_10 = get_period_unutilized(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_11 = get_period_unutilized(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_12 = get_period_unutilized(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<!--********************-->
								
								<td class = "" align="right" style="font-size:10px;">   ${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(get_period_unutilized(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class="body_total" align="center" style="font-size:10px;">${ formatLang((unutulized_1 + unutulized_2 + unutulized_3 + unutulized_4 + unutulized_5 + unutulized_6 + unutulized_7 + unutulized_8 + unutulized_9 + unutulized_10 + unutulized_11 + unutulized_12), digits=get_digits(dp='Budget')) or 0.0}</td>
								<!-- <td align="center" style="font-size:10px;">${ formatLang((unutulized_1 + unutulized_2 + unutulized_3 + unutulized_4 + unutulized_5 + unutulized_6 + unutulized_7 + unutulized_8 + unutulized_9 + unutulized_10 + unutulized_11 + unutulized_12), digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
								
							<tr>
								<td align="center" style="font-size:14px;"></td>
								<td class="line" align="left" colspan="14"></td>
							</tr>
							<!-- ###################################################### -->
							
						%endif
					%else:
						<tr>
							<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
							<td align="left" style="font-size:10px;"></td>
							<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td class="body_total" align="center" style="font-size:10px;">YYY</td>
							<!-- <td align="center" style="font-size:10px;">TOTAL BUDGET</td> -->
							<!-- <td align="center" style="font-size:11px;"></td> -->
						</tr>
					%endif
				
				%endfor
			</table>
		%endfor
	<!-- Non Department -->
	%else: 
		<table width="100% cellpadding="3">
			<tr class ="head_table">
				<td align="center" style="font-size:14px;">No.</td>
				<td align="center" style="font-size:14px;">Account</td>
				<td align="center" style="font-size:14px;">Description</td>
				<td align="center" style="font-size:14px;"><i>${data['form']['1']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['2']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['3']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['4']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['5']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['6']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['7']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['8']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['9']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['10']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['11']['date']}</i></td>
				<td align="center" style="font-size:14px;"><i>${data['form']['12']['date']}</i></td>
				<td align="center" style="font-size:10px;">TOTAL</td>
				<!-- <td align="center" style="font-size:10px;">TOTAL BUDGET</td> -->
				<!-- <td align="center" style="font-size:11px;">REMAINING BUDGET</td> -->
			</tr>
			<%number=0%>
			%for i in get_data(data):
				
				%if data['form']['without_zero']:
					%if i['balance']:
						%if i['type'] == 'view':
							<% bold = 'class="line_table"' %>
						%else:
							<% bold = '' %>
						%endif	
						<tr ${bold}>
							<%number+=1%>
							<td align="center" style="font-size:14px;">${number}</td>
							<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
							<td align="right" style="font-size:10px;">Budget :</td>								
							<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							
							<!--*****-->
							<%total_budget = get_period_budget_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'])%>
								
							<td align="center" style="font-size:10px;"> ${ formatLang(total_budget,digits=get_digits(dp='Budget')) or 0.0}</td>
							<!-- <td align="center" style="font-size:10px;"> ${ formatLang(total_budget,digits=get_digits(dp='Budget')) or 0.0} </td> -->
							<!-- <td align="center" style="font-size:11px;"></td> -->
						</tr>
						<!-- ########################Actual######################## -->
							<tr ${bold}>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" style="font-size:10px;"></td>
								<td align="right" style="font-size:10px;">Actual :</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;"> ${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "row_col_actual" align="right" style="font-size:10px;">	${ formatLang(get_period_actual(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								
								<!--*****-->
								<%total_actual = get_period_actual_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'],)%>
								
								<td align="center" style="font-size:10px;"> ${ formatLang(total_actual,digits=get_digits(dp='Budget')) or 0.0}</td>
								<!-- <td align="center" style="font-size:10px;"> ${ formatLang(total_actual,digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
							<!-- ###################################################### -->
							<!-- ########################Under/ Over######################## -->
							<tr ${bold}>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" style="font-size:10px;"></td>
								<td align="right" style="font-size:10px;">Under/ Over :</td>
								<td align="right" style="font-size:10px;">  ${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period_under(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="center" style="font-size:10px;"> ${ formatLang((total_budget-total_actual),digits=get_digits(dp='Budget')) or 0.0} </td>
								<!-- <td align="center" style="font-size:10px;"> ${ formatLang((total_budget-total_actual),digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
							<!-- ###################################################### -->
							<tr>
								<td align="center" style="font-size:14px;"></td>
								<td class="body_total" align="left" colspan="14"><u>Actual</u></td>
							</tr>
							
							<!-- ########################Actual Transaction######################## -->
							%if data['form']['with_transaction'] and i['type'] == 'normal':
								%for t in get_transaction(data['form']['as_of_date'],i['id']):
									<tr ${bold}>
									
										<!--*****************-->
										<% actual_1 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['1']['start'], data['form']['1']['end'], t['id'],) %>
										<% actual_2 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['2']['start'], data['form']['2']['end'], t['id'],) %>
										<% actual_3 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['3']['start'], data['form']['3']['end'], t['id'],) %>
										<% actual_4 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['4']['start'], data['form']['4']['end'], t['id'],) %>
										<% actual_5 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['5']['start'], data['form']['5']['end'], t['id'],) %>
										<% actual_6 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['6']['start'], data['form']['6']['end'], t['id'],) %>
										<% actual_7 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['7']['start'], data['form']['7']['end'], t['id'],) %>
										<% actual_8 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['8']['start'], data['form']['8']['end'], t['id'],) %>
										<% actual_9 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['9']['start'], data['form']['9']['end'], t['id'],) %>
										<% actual_10 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['10']['start'], data['form']['10']['end'], t['id'],) %>
										<% actual_11 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['11']['start'], data['form']['11']['end'], t['id'],) %>
										<% actual_12 = get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['12']['start'], data['form']['12']['end'], t['id'],) %>
										
										<!--*****************-->
										
										<td align="center" style="font-size:14px;"></td>
										<td align="left" style="font-size:10px;">- ${t.name}</td>
										<td align="right" style="font-size:10px;"></td>
										<td align="right" style="font-size:10px;">  ${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['1']['start'], data['form']['1']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['2']['start'], data['form']['2']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['3']['start'], data['form']['3']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['4']['start'], data['form']['4']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['5']['start'], data['form']['5']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['6']['start'], data['form']['6']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['7']['start'], data['form']['7']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['8']['start'], data['form']['8']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['9']['start'], data['form']['9']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['10']['start'], data['form']['10']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['11']['start'], data['form']['11']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										<td align="right" style="font-size:10px;">	${ formatLang(get_transaction_period(data['form']['as_of_date'],i['id'], data['form']['12']['start'], data['form']['12']['end'], t['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
										
										<td align="center" style="font-size:10px;"> ${ actual_1 + actual_2 + actual_3 + actual_4 + actual_5 + actual_6 + actual_7 + actual_8 + actual_9 + actual_10 + actual_11 + actual_12 } </td>
										<!-- <td align="center" style="font-size:10px;">${ actual_1 + actual_2 + actual_3 + actual_4 + actual_5 + actual_6 + actual_7 + actual_8 + actual_9 + actual_10 + actual_11 + actual_12 }</td> -->
										<!-- <td align="center" style="font-size:11px;"></td> -->
									</tr>
								%endfor
							%endif
							<tr>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" colspan="14"><u>Budget (unutilized)</u></td>
								<td class="body_total" align="center" style="font-size:14px;"></td>
							</tr>
							
							<tr ${bold}>
								<td align="center" style="font-size:14px;"></td>
								<td align="left" style="font-size:10px;">- ${ get_desc_budget_line(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'])}</td>
								<td align="right" style="font-size:10px;"></td>
								
								<!--********************-->
								<%unutulized_1 = get_period_unutilized(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_2 = get_period_unutilized(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_3 = get_period_unutilized(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_4 = get_period_unutilized(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_5 = get_period_unutilized(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_6 = get_period_unutilized(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_7 = get_period_unutilized(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_8 = get_period_unutilized(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_9 = get_period_unutilized(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_10 = get_period_unutilized(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_11 = get_period_unutilized(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<%unutulized_12 = get_period_unutilized(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['1']['end'], i['type'], i['item'])%>
								<!--********************-->
								
								<td class = "" align="right" style="font-size:10px;">   ${ formatLang(unutulized_1,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_2,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_3,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_4,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_5,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_6,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_7,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_8,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_9,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_10,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_11,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td class = "" align="right" style="font-size:10px;">	${ formatLang(unutulized_12,digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="center" style="font-size:10px;">${ formatLang((unutulized_1 + unutulized_2 + unutulized_3 + unutulized_4 + unutulized_5 + unutulized_6 + unutulized_7 + unutulized_8 + unutulized_9 + unutulized_10 + unutulized_11 + unutulized_12), digits=get_digits(dp='Budget')) or 0.0}</td>
								<!-- <td align="center" style="font-size:10px;">${ formatLang((unutulized_1 + unutulized_2 + unutulized_3 + unutulized_4 + unutulized_5 + unutulized_6 + unutulized_7 + unutulized_8 + unutulized_9 + unutulized_10 + unutulized_11 + unutulized_12), digits=get_digits(dp='Budget')) or 0.0}</td> -->
								<!-- <td align="center" style="font-size:11px;"></td> -->
							</tr>
								
							<tr>
								<td align="center" style="font-size:14px;"></td>
								<td class="line" align="left" colspan="14"></td>
							</tr>
							<!-- ###################################################### -->
					%endif
				%else:
					<tr ${bold}>
						<%number+=1%>
						<td align="center" style="font-size:14px;">${number}</td>
						<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
						<td align="right" style="font-size:10px;">Budget :</td>								
						<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of_date'],data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of_date'],data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						<td align="center" style="font-size:104px;">UUU</td>
						<!-- <td align="center" style="font-size:10px;">TOTAL BUDGET</td> -->
						<!-- <td align="center" style="font-size:10px;"></td> -->
					</tr>
				%endif
			
			%endfor
		</table>
	%endif
	
		
	<br/>
	
</body>
</html>