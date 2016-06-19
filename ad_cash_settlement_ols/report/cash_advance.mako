<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<style>
			.break { page-break-after: always; }
			h1{
				text-align: center;
			}
			table { 
			    border-collapse: collapse; 
				page-break-inside:auto;
			}
			tr
			{
				border-bottom: 1px solid;
				border-color: rgb(160,160,255);
				page-break-inside:avoid;
				page-break-after:auto;
			}
			table tr td{
				padding-right: 15px;
			}
		</style>
	</head>
	<% setLang('en_US' or 'en_ID' ) %>
	<body>
		<h1>Cash Advance</h1>
		<table class="break" width=100% border="0" cellscpacing="0" style="font-family:arial;font-size:12px;";>
			<tr>
				<th>Advance Method</th>
				<th>Employee</th>
				<th>Memo</th>
				<th>Advance Date</th>
				<th>Number</th>
				<th>Total</th>
				<th>State</th>
			</tr>
			<% amount = 0.00 %>
			%for o in get_object(data):
			<tr>
				<td>
					%if o.advance_method == 'general':
						General
					%elif o.advance_method == 'travel':
						Travel
					%elif o.advance_method == '':

					%endif
				</td>
				<td>
					${o.employee_id.name or ''}
					${o.employee_id.nik or ''}
				</td>
				<td>${o.name or ''}</td>
				<td>
					<% date = change_format_date(o.date) %>
					${date}
				</td>
				<td>${o.number or ''}</td>
				<td>${formatLang(o.amount or '',digits=get_digits(dp='Purchase Price'))}</td>
				<% amount += o.amount %>
				<td>
					%if o.state == 'draft':
						Draft
					%elif o.state == 'approve':
						Waiting Head of Division Approve
					%elif o.state == 'approve2':
						Waiting CEO Approve
					%elif o.state == 'approve2-1':
						Waiting HRD Approve
					%elif o.state == 'approve3':
						Waiting Treasury Approve
					%elif o.state == 'approve4':
						Waiting CFO Approve
					%elif o.state == 'posted':
						Posted
					%elif o.state == 'cancel':
						Cancelled
					%elif o.state == '':

					%endif
				</td>
			</tr>
			%endfor
			<tr>
				<td colspan="5"><strong>Total</strong></td>
				<td colspan="2"><strong>${formatLang(amount or '',digits=get_digits(dp='Purchase Price'))}</strong></td>
			</tr>
		</table>
	</body>
</html>