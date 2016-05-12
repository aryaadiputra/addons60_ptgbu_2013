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
			<th align="left" style="font-size:10px;">Budget Rolling Report (Detail)</th>
		</tr>
	</table>
	%if len(get_department(data))>0: 
		%for d in get_department(data):
			<table width="100% cellpadding="3" class="break">
				<tr>
					<td colspan="14"><h2>${d.name}</h2></td>
				</tr>
				<tr class ="head_table">
					<td align="center" style="font-size:14px;"></td>
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
				</tr>
				<tr class ="head_table">
					<td align="center" style="font-size:14px;"></td>
					<td align="center" style="font-size:14px;">0</td>
					<td align="center" style="font-size:14px;">${data['form']['1']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['2']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['3']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['4']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['5']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['6']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['7']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['8']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['9']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['10']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['11']['state']}</td>
					<td align="center" style="font-size:14px;">${data['form']['12']['state']}</td>
				</tr>
				%for i in get_data(data):
					
					%if data['form']['without_zero']:
						%if i['balance']:
							%if i['type'] == 'view':
								<% bold = 'class="line_table"' %>
							%else:
								<% bold = '' %>
							%endif	
							<tr ${bold}>
								<td align="left" style="font-size:10px;"></td>
								<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
								<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
								<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], d['id']),digits=get_digits(dp='Budget')) or 0.0}</td>
							</tr>
							%if data['form']['with_transaction'] and i['type'] == 'normal':
								%for t in get_transaction(i['id'],d['id']):
									<tr>
										<td colspan="12">${t.name}</td>
										<td >${t.amount}</td>
										<td >${t.date}</td>
									</tr>
								%endfor
							%endif
						%endif
					%else:
						<tr>
							<td align="left" style="font-size:10px;"></td>
							<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
							<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						</tr>
					%endif
				
				%endfor
			</table>
		%endfor
	%else: 
		<table width="100% cellpadding="3">
			<tr class ="head_table">
				<td align="center" style="font-size:14px;"></td>
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
			</tr>
			<tr class ="head_table">
				<td align="center" style="font-size:14px;"></td>
				<td align="center" style="font-size:14px;"></td>
				<td align="center" style="font-size:14px;">${data['form']['1']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['2']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['3']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['4']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['5']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['6']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['7']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['8']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['9']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['10']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['11']['state']}</td>
				<td align="center" style="font-size:14px;">${data['form']['12']['state']}</td>
			</tr>
			%for i in get_data(data):
				
				%if data['form']['without_zero']:
					%if i['balance']:
						%if i['type'] == 'view':
							<% bold = 'class="line_table"' %>
						%else:
							<% bold = '' %>
						%endif	
						<tr ${bold}>
							<td align="left" style="font-size:10px;"></td>
							<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
							<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
						</tr>
						%if data['form']['with_transaction'] and i['type'] == 'normal':
							%for t in get_transaction(i['id']):
								<tr>
									<td colspan="12">${t.name}</td>
									<td >${t.amount}</td>
									<td >${t.date}</td>
								</tr>
							%endfor
						%endif
					%endif
				%else:
					<tr>
						<td align="left" style="font-size:10px;"></td>
							<td align="left" style="font-size:10px;font-color:white;"><span style="font-color:#000000;font-size:8px;">${ '&nbsp;&nbsp;&nbsp;'*(i['level']) }</span><span style="font-size:8px;">${ i['name'] }</span></td>
							<td align="right" style="font-size:10px;">  ${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
							<td align="right" style="font-size:10px;">	${ formatLang(get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item']),digits=get_digits(dp='Budget')) or 0.0}</td>
					</tr>
				%endif
			
			%endfor
		</table>
	%endif
	
		
	<br/>
	
</body>
</html>