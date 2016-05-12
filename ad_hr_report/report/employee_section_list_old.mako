<html>
	<head>
	<style>
		.no{text-align:right;}
		.no{text-align:right;}
		.nik{text-align:left;}
		.name{text-align:left;}
		.type{text-align:left;}
		.state{text-align:left;}
		.age{text-align:right;}
	</style>
	</head>
	<body>
	<center><h2>Employee List</h2></center>
	<% 
	dummy=False
	datalist=data['form'] 
	%>
	<table width="100%" border="1">
		<tr>
			<th rowspan="2" valign="top">No</th>
			<th class="nik">NIK</th>
			<th class="name">Name</th>
			<th class="type">Placement</th>
			<th class="state">State</th>
			<th class="age">Age (Years)</th>
		</tr>
	<% sections=get_section(dummy,datalist['filter_sect']) %>
	%for section in sections:
		<tr>
			<td></td>
			<td colspan="5"><b>Section :${section.name}</b></td>
		</tr>
		<% 
		dept=get_dept(section.department.id)
		%>
		%if dept:
			<tr>
				<td colspan="2"></td>
				<td colspan="4"><b>Department : ${dept.name}</b></td>
			</tr>
			<% no=1 %>
			<% employees=get_employee(datalist['active'],[dept.id],[section.id])%>
			%if len(employees)>0:
				%for emp in employees:
					<tr>
						<td class="no">${no}</td>
						<td class="nik">${emp.nik}</td>
						<td class="name">${emp.name}</td>
						<td class="type">${emp.type.upper()}</td>
						<td class="state">${emp.resource_id.active and "Active" or "Non Active"}</td>
						<td class="age">${emp.age}</td>
					</tr>
					<% no+=1 %>
				%endfor
			%else:
				<tr>
					<td colspan="6" align="center">No Employee defined in this section</td>
				</tr>
			%endif
			<tr><td colspan="6">&nbsp;</td></tr>
		%else:
			<% employees=get_employee(datalist['active'],dummy,[section.id])%>
			%if employees>0:
				%for emp in employees:
					<tr>
						<td class="no">${no}</td>
						<td class="nik">${emp.nik}</td>
						<td class="name">${emp.name}</td>
						<td class="type">${emp.type.upper()}</td>
						<td class="state">${emp.resource_id.active and "Active" or "Non Active"}</td>
						<td class="age">${emp.age}</td>
					</tr>
					<% no+=1 %>
				%endfor
			%else:
				<tr>
					<td colspan="5" align="center">No Employee defined in this department</td>
				</tr>
			%endif
		<tr><td colspan="6">&nbsp;</td></tr>
		%endif			
	%endfor
	</table>
	<p style="page-break-after:always"></p>
	</body>
</html>