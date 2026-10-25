# Deployment

Status: NOT SET UP.  Nothing has been created in AWS and DNS is unchanged.

docs.joulescope.com is static files in a private S3 bucket behind
CloudFront, set up like download.joulescope.com.  GitHub Actions deploys
with short-lived OIDC credentials, so no AWS keys are stored anywhere.

```
GitHub Actions (deploy.yml, "production" environment, reviewer approval)
   │  OIDC token: repo:jetperch/joulescope_docs:environment:production
   ▼
IAM role joulescope-docs-deploy
   │  s3 sync                           cloudfront:CreateInvalidation
   ▼                                                 ▼
S3 bucket (private) ◀── Origin Access Control ── CloudFront ◀── viewers
                                               (docs.joulescope.com)
```

The steps use the AWS CLI so that every permission is written down.  The
policies and the distribution are templates in `infra/`; `envsubst` fills in
the values.  Each step ends with a check, so a mistake shows up where it
happens instead of at the first deploy.


## 0. Prerequisites

### joulescope_docs on GitHub, with submodules

The deploy workflow publishes the artifacts of a green `ci` run, and CI
checks out the projects as submodules.  During development `external/` held
plain clones.  First check that each clone has nothing left to push:

```bash
cd joulescope_docs
for r in external/*; do git -C "$r" status -sb | head -1; done   # no "ahead"
```

Then replace the clones with submodules and publish the repository:

```bash
sed -i '/^\/external\/$/d' .gitignore
rm -rf external
git submodule add https://github.com/jetperch/joulescope_driver external/joulescope_driver
git submodule add https://github.com/jetperch/pyjoulescope external/pyjoulescope
git submodule add https://github.com/jetperch/jls external/jls
git submodule add https://github.com/jetperch/pyjoulescope_ui external/pyjoulescope_ui
git add -A
git commit -m "Initial joulescope_docs"
gh repo create jetperch/joulescope_docs --private --source . --push
```

Wait for a green `ci` run (Actions tab).  `deploy` publishes that run's
`site` and `pdf` artifacts.

### Tools and shell variables

* AWS CLI v2, signed in with permission to create S3, ACM, CloudFront and
  IAM resources: `aws sts get-caller-identity` works.
* `envsubst` (Ubuntu package `gettext-base`) and `gh`, signed in.

Set these in the shell you use for every step:

```bash
export AWS_REGION=us-east-1                    # CloudFront certificates live here
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export DOMAIN=docs.joulescope.com
export BUCKET=docs-joulescope-com     # globally unique, no dots
export GITHUB_REPO=jetperch/joulescope_docs     # exactly as on GitHub
mkdir -p build/aws
```

The bucket name has no dots.  Dotted names do not match the wildcard TLS
certificate of `*.s3.amazonaws.com`.

Later steps print IDs that you `export` in the same shell.  Keep a note of
them; GitHub needs four of them in step 8.

To copy what download.joulescope.com does, look at its distribution:

```bash
aws cloudfront list-distributions --query \
    "DistributionList.Items[].{id:Id,aliases:Aliases.Items,origin:Origins.Items[0].DomainName}"
aws cloudfront get-distribution-config --id <download distribution id>
```


## 1. S3 bucket

```bash
aws s3api create-bucket --bucket "$BUCKET" --region "$AWS_REGION"
aws s3api put-public-access-block --bucket "$BUCKET" \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket "$BUCKET" \
    --versioning-configuration Status=Enabled
aws s3api put-bucket-lifecycle-configuration --bucket "$BUCKET" \
    --lifecycle-configuration '{"Rules": [{"ID": "expire-old-versions",
      "Status": "Enabled", "Filter": {},
      "NoncurrentVersionExpiration": {"NoncurrentDays": 90}}]}'
```

Versioning lets you recover from a bad `--delete` sync; the lifecycle rule
drops old versions after 90 days.  Outside us-east-1, `create-bucket` also
needs `--create-bucket-configuration LocationConstraint=$AWS_REGION`.

Check: `aws s3api get-public-access-block --bucket "$BUCKET"` shows all four
settings `true`.


## 2. TLS certificate (ACM, us-east-1)

First look for an existing certificate that already covers the name, such
as a `*.joulescope.com` wildcard used by download.joulescope.com:

```bash
aws acm list-certificates --region us-east-1 \
    --query "CertificateSummaryList[].[DomainName,CertificateArn]" --output table
```

If one covers docs.joulescope.com, `export CERT_ARN=<its ARN>` and go to
step 3.  Otherwise request one:

```bash
export CERT_ARN=$(aws acm request-certificate --region us-east-1 \
    --domain-name "$DOMAIN" --validation-method DNS \
    --query CertificateArn --output text)
aws acm describe-certificate --region us-east-1 --certificate-arn "$CERT_ARN" \
    --query "Certificate.DomainValidationOptions[0].ResourceRecord"
```

Add the printed CNAME record at the DNS provider for joulescope.com.  If
Route 53 hosts the zone, `aws route53 list-hosted-zones-by-name --dns-name
joulescope.com` finds it.  Then wait, usually a few minutes:

```bash
aws acm wait certificate-validated --region us-east-1 --certificate-arn "$CERT_ARN"
```

Check: `aws acm describe-certificate --region us-east-1 --certificate-arn
"$CERT_ARN" --query Certificate.Status` prints `"ISSUED"`.  This validation
record only proves ownership; the site's own DNS record comes last (step 9).


## 3. CloudFront Function (directory index)

The private S3 origin has no index documents, so `/products/` must become
`/products/index.html`.  `infra/cloudfront-index.js` does that, and
`tests/test_cloudfront.py` tests it.

```bash
aws cloudfront create-function --name docs-joulescope-index \
    --function-config 'Comment=docs.joulescope.com directory index,Runtime=cloudfront-js-2.0' \
    --function-code fileb://infra/cloudfront-index.js
ETAG=$(aws cloudfront describe-function --name docs-joulescope-index \
    --query ETag --output text)
aws cloudfront publish-function --name docs-joulescope-index --if-match "$ETAG"
export FUNCTION_ARN=$(aws cloudfront describe-function --name docs-joulescope-index \
    --stage LIVE --query FunctionSummary.FunctionMetadata.FunctionARN --output text)
```

To change the function later, run `update-function` with the current ETag,
then `publish-function` again.


## 4. Origin Access Control

```bash
export OAC_ID=$(aws cloudfront create-origin-access-control \
    --origin-access-control-config '{"Name": "docs-joulescope-com",
      "SigningProtocol": "sigv4", "SigningBehavior": "always",
      "OriginAccessControlOriginType": "s3"}' \
    --query OriginAccessControl.Id --output text)
```


## 5. CloudFront distribution

`infra/distribution-config.json` uses the managed **CachingOptimized** cache
policy, redirects HTTP to HTTPS, compresses, and attaches the function from
step 3.

```bash
envsubst < infra/distribution-config.json > build/aws/distribution-config.json
grep -n '\${' build/aws/distribution-config.json      # must print nothing
aws cloudfront create-distribution \
    --distribution-config file://build/aws/distribution-config.json \
    --query "Distribution.[Id,DomainName]" --output text
export DIST_ID=<first value, like E2ABCDEFGHIJKL>
export DIST_DOMAIN=<second value, like d1234abcd.cloudfront.net>
aws cloudfront wait distribution-deployed --id "$DIST_ID"   # several minutes
```

If `grep` prints a line, a variable from an earlier step is not exported.


## 6. Bucket policy

Only this distribution may read the bucket.  The `s3:ListBucket` statement
makes missing pages return 404 instead of 403.

```bash
envsubst < infra/bucket-policy.json > build/aws/bucket-policy.json
aws s3api put-bucket-policy --bucket "$BUCKET" \
    --policy file://build/aws/bucket-policy.json
```

Check.  The bucket is still empty, so expect 404:

```bash
curl -sI "https://$DIST_DOMAIN/" | head -1
```

A 403 means the bucket policy, the OAC or the distribution ID is wrong.


## 7. GitHub OIDC provider and deploy role

### OIDC provider (once per AWS account)

```bash
aws iam list-open-id-connect-providers
```

If no ARN ends in `token.actions.githubusercontent.com`, create it:

```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com
```

Older AWS CLI versions insist on `--thumbprint-list`.  IAM no longer uses the
thumbprint for GitHub (it trusts GitHub's certificate authority directly), so
any 40-character hex value satisfies the CLI.

### Role

The trust policy accepts only tokens for this repository's `production`
environment.  Other repositories, branches, pull requests, and jobs without
that environment cannot assume the role.

```bash
envsubst < infra/deploy-role-trust.json > build/aws/deploy-role-trust.json
envsubst < infra/deploy-role-policy.json > build/aws/deploy-role-policy.json
aws iam create-role --role-name joulescope-docs-deploy \
    --description "GitHub Actions deploy for docs.joulescope.com" \
    --assume-role-policy-document file://build/aws/deploy-role-trust.json
aws iam put-role-policy --role-name joulescope-docs-deploy \
    --policy-name deploy-docs \
    --policy-document file://build/aws/deploy-role-policy.json
export ROLE_ARN=$(aws iam get-role --role-name joulescope-docs-deploy \
    --query Role.Arn --output text)
```

The role can list the bucket, read, write and delete its objects, and
invalidate this one distribution.  Nothing else.

Check the trust policy subject:

```bash
aws iam get-role --role-name joulescope-docs-deploy \
    --query "Role.AssumeRolePolicyDocument.Statement[0].Condition"
```

The `sub` must be exactly
`repo:jetperch/joulescope_docs:environment:production`.


## 8. GitHub environment and variables

```bash
gh api -X PUT "repos/$GITHUB_REPO/environments/production"
for v in "AWS_DEPLOY_ROLE_ARN=$ROLE_ARN" "AWS_REGION=$AWS_REGION" \
         "DOCS_BUCKET=$BUCKET" "CLOUDFRONT_DISTRIBUTION_ID=$DIST_ID"; do
  gh variable set "${v%%=*}" --env production --repo "$GITHUB_REPO" --body "${v#*=}"
done
gh variable list --env production --repo "$GITHUB_REPO"
```

These are variables, not secrets: none of them grants access on its own.
They must be on the `production` environment, which `deploy.yml` uses.

Then, in the repository's **Settings → Environments → production**:

* **Required reviewers**: add yourself and anyone else who may publish.
* **Deployment branches and tags**: selected branches, `main` only.


## 9. First deploy, then DNS

1. Run the `deploy` workflow (Actions → deploy → Run workflow) with the run
   id of a green `ci` run on `main`.  The run id is the number in the run's
   URL.  Approve the deployment when asked.
2. Check the site on the CloudFront domain:

   ```bash
   for p in / /products/ /products/js320 /products/js320/fuse.html \
            /software/joulescope_driver/h_jsdrv.html /llms.txt \
            /products/datasheets/js320.yaml /pdf/js320_users_guide.pdf \
            /no/such/page.html; do
     printf '%-45s ' "$p"
     curl -s -o /dev/null -w '%{http_code} %{content_type}\n' "https://$DIST_DOMAIN$p"
   done
   ```

   Expect 200 for every path except `/products/js320` (301 to the
   directory) and the last one (404).  The YAML must be `text/yaml`.
3. Point DNS at CloudFront (separate approval):
   * Route 53: alias A and AAAA records `docs.joulescope.com` → the
     distribution.
   * Other DNS: a CNAME `docs.joulescope.com` → `$DIST_DOMAIN`.
4. Check `https://docs.joulescope.com/` once DNS has propagated.


## Updating the site

1. Merge to `main` and wait for a green `ci` run.
2. Run `deploy` with that run's id, plus an `archive_run_id` to publish a
   release archive, and approve it.

The sync uses `--delete` but excludes `archive/*`, so published archives are
never removed, and publishing an archive that exists fails.  Browsers cache
pages for 5 minutes and archives for a day.  Every deploy invalidates
CloudFront.


## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | The token's `sub` does not match the trust policy.  Check the repository name (case, `_`), that the job uses `environment: production`, and that the organization has not customized the subject claim: `gh api orgs/jetperch/actions/oidc/customization/sub`. |
| `Could not load credentials from any providers` | The workflow lacks `permissions: id-token: write`, or `AWS_DEPLOY_ROLE_ARN` is empty because the variable is on the repository instead of the `production` environment. |
| `AccessDenied` on `ListObjectsV2` during `s3 sync` | `s3:ListBucket` must be on the bucket ARN (`arn:aws:s3:::bucket`), not `bucket/*`. |
| `AccessDenied` on `PutObject` or `DeleteObject` | The object statement must use `arn:aws:s3:::bucket/*`, and `DOCS_BUCKET` must match the real bucket. |
| `AccessDenied` on `CreateInvalidation` | CloudFront ARNs have no region: `arn:aws:cloudfront::ACCOUNT:distribution/ID`. |
| 403 for every page | The bucket policy's `AWS:SourceArn` does not name this distribution, or the origin has no OAC attached. |
| 403 instead of 404 for missing pages | The bucket policy lacks the `s3:ListBucket` statement. |
| `/products/` fails but `/products/index.html` works | The CloudFront Function is not published (`--stage LIVE`) or not attached to the default cache behavior. |
| Old pages or images after a deploy | The invalidation is still running (a minute or two), or the browser cache (up to 5 minutes; Ctrl+Shift+R). |
| `InvalidViewerCertificate` | The certificate is not in us-east-1, not yet ISSUED, or does not cover docs.joulescope.com. |
| `CNAMEAlreadyExists` | Another distribution already has the alias.  Remove it there first. |
| YAML downloads instead of displaying | The deploy's YAML copy step did not run; it sets `text/yaml`. |


## Cutover checklist (after DNS)

1. Read the Docs projects `joulescope`, `joulescope-driver` and `jls`: keep
   them as the reference for old releases (decision D3).  Optionally add a
   banner or redirect for `latest` that points to docs.joulescope.com.
2. Replace `download.joulescope.com/products/joulescope_ui/users_guide/`,
   which printed guides link to, with a redirect to
   `https://docs.joulescope.com/software/joulescope_ui/`.
3. Update the package `project_urls` to docs.joulescope.com in each
   project's next release.
4. Done 2026-10-25: the project documentation changes are pushed.  The
   driver README and the pyjoulescope docs link to the Supported platforms
   section, which works once DNS points here.
