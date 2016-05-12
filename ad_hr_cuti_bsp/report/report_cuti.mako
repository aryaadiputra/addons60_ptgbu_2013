<html>
<head>
</head>
<body>
	<center>
	<h3>Off-Day's Summary</h3>
	<br>
	<h4>Analyze from ${data['form']['start_date']} to ${data['form']['end_date']} of the Validated Holidays</h4>
	</center>
<table border="1" style="border-collapse:collapse;">
	<tr>
		<td rowspan="2">Month</td>
		${get_colspan_month(data['form']['start_date'],data['form']['end_date'])}
	</tr>
	<tr>
		%for i in track_days(data['form']['start_date'],data['form']['end_date']):
			<td>${i}</td>
		%endfor
	</tr>
	<tr>
		<td>Employees</td>
		%for j in track_date(data['form']['start_date'],data['form']['end_date']):
			<td>${j['d']}</td>
		%endfor
	</tr>
	%for o in get_employees_data(data['form']['start_date'],data['form']['end_date'],data['form']['employee_id']):
		<tr>
			<td>[${o['nik']}] ${o['name']}</td>
			%for k in track_date(data['form']['start_date'],data['form']['end_date']):
				%if o['cuti'].has_key(k['date']):
					<td>${o['cuti'][k['date']]}</td>
				%else:
					<td></td>
				%endif
			%endfor
		</tr>
	%endfor
</table>
</body>
</html>