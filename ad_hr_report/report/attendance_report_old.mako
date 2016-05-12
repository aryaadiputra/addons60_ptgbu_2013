<html>
	<head>
	<%
	import addons
	%>
	</head>
	<body>
		<% form=data['form'] %>
		<center>
			<h3>Employee Attendance Report</h3>
			<h5>Date : ${form['date_print']}</h5>
		</center>
		<table>
			<tr>
				<td>No</td>
				<td>NIK</td>
				<td>Name</td>
				<td>Sign In</td>
				<td>Sign Out</td>
				<td>Working time</td>
				<td>Status</td>
			</tr>
			<% n=1 %>
			%for emp in get_employee(form['employee_ids']):
				<tr>
				<td>${n}</td>
				<td>${emp.nik}</td>
				<td>${emp.name}</td>
				<% counter=0 %>
				%for worktime in get_work_time(emp.id,form['date_print']):
					%if counter==0:
						<td>${worktime['sign_in'] and worktime['sign_in'] or ''}</td>
						<td>${worktime['sign_out'] and worktime['sign_out'] or ''}</td>
						<td>Working Time</td>
						<td>State</td>
					%else:
						<tr>
							<td>${n}</td>
							<td>${emp.nik}</td>
							<td>${emp.name}</td>
							<td>${worktime['sign_in'] and worktime['sign_in'] or ''}</td>
							<td>${worktime['sign_out'] and worktime['sign_out'] or ''}</td>
							<td>Working Time</td>
							<td>State</td>
						</tr>
					%endif
					<%counter+=1%>
				%endfor
				<%n+=1%>
				</tr>
			%endfor
			
		</table>
	</body>
</html>