TERRAFORM = terraform -chdir=.

bootstrap:
@echo "🔧  Creating remote state bucket…"
gsutil mb -p $(PROJECT_ID) -l $(REGION) gs://tfstate-crypto-options-algo || true
gsutil versioning set on gs://tfstate-crypto-options-algo

init:
$(TERRAFORM) init

plan:
$(TERRAFORM) plan -var "project_id=$(PROJECT_ID)"

apply:
$(TERRAFORM) apply -auto-approve -var "project_id=$(PROJECT_ID)"

destroy:
$(TERRAFORM) destroy -auto-approve -var "project_id=$(PROJECT_ID)"
