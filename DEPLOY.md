# 部署到 Kubernetes 集群（JianyueLab Talos）

vBook 是 **SSR + 有状态** app（Astro Node standalone + Postgres + Drizzle 迁移 + AI 密钥），
按 k8s 仓库 `docs/adding-a-web-app.md` 的「有状态 app」配方部署。CI（[.github/workflows/deploy.yaml](.github/workflows/deploy.yaml)）
在每次 push 到 `main` 时：构建镜像 → 推送 GHCR → 同步密钥 → **跑迁移 Job** → 滚动更新。

- 域名：`ebook.ustb.world`
- 镜像：`ghcr.io/ijunecn/vbook`
- namespace：`vbook`
- 数据库：CNPG `vbook-db`（2 实例，R2 备份 `s3://k8s/vbook`），连接串自动生成进 `vbook-db-app` 密钥

> ⚠️ 运行时密钥通过 `process.env` 在容器里注入（**不是** `import.meta.env`，那个会在 build 时把值写死进镜像）。详见 [CLAUDE.md](CLAUDE.md) 的 Environment 段。

---

## 一次性准备（用 admin kubeconfig，从 k8s 仓库执行）

```bash
export KUBECONFIG=/Users/jhl/Documents/Dev/k8s/kubeconfig

# 1) namespace + 把已有 deployer SA 授权到 vbook namespace
kubectl apply -f /Users/jhl/Documents/Dev/vBook/k8s/namespace-rbac.yaml

# 2) R2 备份凭据（复用现有 R2 API Token，别 commit）
kubectl -n vbook create secret generic r2-backup-creds \
  --from-literal=ACCESS_KEY_ID='<R2_ACCESS_KEY_ID>' \
  --from-literal=ACCESS_SECRET_KEY='<R2_SECRET_ACCESS_KEY>'

# 3) 改 k8s/postgres-cluster.yaml 里的 <R2_ACCOUNT_ID>，然后建 CNPG 集群
kubectl apply -f /Users/jhl/Documents/Dev/vBook/k8s/postgres-cluster.yaml
kubectl -n vbook get cluster,pods -w   # 等 vbook-db Phase=healthy、2 个 pod Ready
```

> 前置（集群级，已装则跳过）：CNPG operator + barman-cloud 插件（`cnpg-system`）、cert-manager、`local-path` StorageClass。

## GitHub 仓库 Secret（Settings → Secrets and variables → Actions）

`iJunecn/vBook` 是**个人仓库**（不在 JianyueLab-Org 组织里），所以**四个都要在仓库级**设置：

| Secret | 值 |
|---|---|
| `KUBECONFIG_B64` | 受限 `deployer` kubeconfig 的 base64（与其他 app 复用同一值）。`base64 -w0 deployer-kubeconfig` |
| `GHCR_PULL_TOKEN` | PAT，需 `read:packages`，能拉 `ghcr.io/ijunecn/*`（个人命名空间的私有包） |
| `AGNES_API_KEY` | AI 接口 key |
| `AGNES_BASE_URL` | AI 接口 base（以 `/v1` 结尾） |

## DNS

在 `ustb.world` 加 A 记录指向两个入口节点（轮询；要真高可用见 k8s 仓库文档的「入口高可用」）：

```
ebook.ustb.world.  A  208.68.182.133   (ty1)
ebook.ustb.world.  A  208.68.182.131   (ty4)
```

---

## 上线 & 验证

push 到 `main`（或 Actions 里手动 `workflow_dispatch`）→ 自动构建+迁移+部署。

```bash
export KUBECONFIG=/Users/jhl/Documents/Dev/k8s/kubeconfig
kubectl -n vbook get pods,ingress
kubectl -n vbook get certificate         # READY=True 表示 HTTPS 证书签好
kubectl -n vbook logs job/vbook-migrate   # 迁移输出
curl -I https://ebook.ustb.world
```

## 排错

- **Pod ImagePullBackOff** → `GHCR_PULL_TOKEN` 没配或无 `read:packages`。
- **迁移 Job 失败** → CI 会打印 `kubectl logs job/vbook-migrate`；多半是 `DATABASE_URL`/CNPG 没就绪。
- **证书一直 not ready** → DNS 没生效或没指对节点；`kubectl -n vbook describe certificate web`、`kubectl get challenges -A`。
- **Deploy 步骤报权限错** → 漏了步骤 1 的 RoleBinding。
- **改了 AGNES 密钥不生效** → 改 GitHub Secret 后重跑 workflow（密钥由 CI 托管，启动时注入，需重新部署）。
