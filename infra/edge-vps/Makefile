.PHONY: init plan apply destroy

init:
	terraform init

plan:
	terraform plan -var-file=variables.tfvars

apply:
	terraform apply -var-file=variables.tfvars -auto-approve

destroy:
	terraform destroy -var-file=variables.tfvars -auto-approve

output:
	terraform output
