# SOC �Խ�ȫ��· �� Multi-Agent ִ�� Prompt

> **��;**��auto-dev-orchestrator ��ȡ�󣬰� Wave �ɷ� Task ���� Agent ִ�С�
> **ǰ��**��PRD ����ͨ�����û��ظ���ͬ��ִ�С���
> **PRD**��`svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md`
> **�������**��`svmp/docs/internal/features/soc-link-task-matrix.yaml`

---

## ͨ��Լ�������� Agent �ض���

1. **��ѭ Skill**��`esmp-backend-dev`��DDD �Ĳ㣩��`esmp-rd-standards`������/Git �淶��
2. **���������**��`.cursor/rules/backend-framework-context.mdc`��spore-base-ddd��
3. **�ο�ʵ��**��`project_backend/svmp/vul-pass/`��������·����`project_backend/framework/asset/esmp-starters/esmp-starter-task/`��DDD ��׼��
4. **DDL ��ʽ**��Liquibase Groovy �ű������� `src/main/resources/db/mysql/` ��
5. **Feign �ͻ���**������������ Feign��·�� `/internal/open/v1/**`����Ⱥ�ڰ�������Ȩ
6. **��ֹ**���� `transition` ״̬�������߼����� `clover-front/**`����ըɾ�� `MsgSend*`
7. **�ύ�淶**��`feat(scope): xxx` / `fix(scope): xxx`���ο� `esmp-rd-standards`

---

## Wave 1 ִ�� Prompt��3 ��� Agent + 1 ǰ�� Agent ���У�

### Agent 1: vuln-task-center API ����

```text
���� vuln-task-center ��˿��� Agent��

## ����
�� project_backend/svmp/vuln-task-center ���� 4 �� REST API���� vul-pass ��ȡɨ���������ɱ��档

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md�����壩
2. svmp/docs/internal/vuln-task-center-ɨ����������-PRD.md����3.3.1, ��3.0 ����뱨����
3. .cursor/skills/esmp-backend-dev/SKILL.md

## �ض�����
1. project_backend/svmp/vuln-task-center/ �µ� ScanTaskUi.java��ScanTaskAppServiceImpl.java
2. project_backend/svmp/vuln-task-center/ �µ� ScanSubTaskDO.java
3. project_backend/svmp/vuln-task-center/ �µ� MsgSendLM.java��VulnTaskListenerLM.java������ LM �߼���

## ������
### 1. GET /v1/scan/task/survey/{surveyId}/results
- ·������: surveyId
- ��Ӧ data: { surveyId, status, targets[], liveProbeResults[], portScanResults[], vulnerabilities[], weakPasswords[], baselineResults[] }
- targets[] Ԫ��: { targetId, target, targetType, assetID, assetName, os }
- liveProbeResults[] Ԫ��: { liveProbeId, targetId, address, alive, probeMethod, latencyMs, mac, osGuess, detectedAt }
- portScanResults[] Ԫ��: { portScanId, targetId, address, port, protocol, state, service, banner, version, detectedAt }
- vulnerabilities[] Ԫ��: { vulID, orgVulId, vulLevel, vulName, vulDesc, instances[] }
- instances[] Ԫ��: { vulInfoID, targetId, vulInfoStat, vulNetAddr, vulPort, vulSvc, isAccess, transferTime, evidence }

ʵ��Ҫ��:
- ScanResultUi.java��UI �㣩
- ScanResultAppServiceImpl.java��App �㣬�ۺ����� scan_sub_task ������ݣ�
- �������� VulnTaskListenerLM/AH �Ľ�������߼�
- ����Ʒ©�� vulID �ۺϣ�ʵ������ instances[]

### 2. POST /v1/scan/task/survey/{surveyId}/report/generate
- ������: { reportTemplateCode?, format? }
- ��Ӧ data: { reportJobId, status }
- �첽���ɣ����� queued

### 3. GET /v1/scan/report/jobs/{reportJobId}
- ��Ӧ data: { reportJobId, status, progress, downloadUrl? }
- status: pending/queued/generating/ready/failed

### 4. GET /v1/scan/report/jobs/{reportJobId}/download
- ���ض������ļ���

### 5. report_job ���Liquibase��
- �ֶ�: id, survey_id, sub_task_id, report_template_code, format, status, progress, file_path, file_name, file_format, content_type, byte_size, checksum, error_message, created_at, updated_at, expires_at

### 6. Kafka ������
- SubTaskStatusEventProducer: ������״̬���ʱ����
  ��Ϣ��: { event:"SUB_TASK_STATUS_CHANGED", surveyId, subTaskId, vendor, status, progress, finishedAt, passTaskId, passSubTaskId }
- ReportJobEventProducer: �������ʱ����
  ��Ϣ��: { event:"REPORT_JOB_COMPLETED", reportJobId, surveyId, status, downloadUrl, passTaskId }

## Լ��
- DDD �Ĳ�: Ui �� App �� Domain �� Infra
- ��Ϣ����뺬 passTaskId �� passSubTaskId�����·�ʱ���룩
- report_job ״̬��: pending��queued��generating��ready/failed
- mvn compile ����ͨ��

## ����
- [ ] 4 �� API ����
- [ ] results ���������ṹ
- [ ] report �����첽���ɲ����
- [ ] Kafka ��Ϣ����
- [ ] Liquibase ���ظ�ִ��
```

### Agent 2: vul-pass OpenTaskOrchestrator ����

```text
���� vul-pass ��˿��� Agent��

## ����
�� project_backend/svmp/vul-pass ���� OpenTaskOrchestrator��ʵ�� SOC_DUAL ˫ɨ���š�

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md��������
2. svmp/docs/internal/open-api-vtc-pass-��ط���.md�����塢���������ߣ�
3. svmp/docs/internal/©��ʵ������������˫��洢-��ط���.md�����ģ�

## �ض�����
1. project_backend/svmp/vul-pass/ �µ� VulScanTaskUi.java�����б�����ڣ�
2. project_backend/svmp/vul-pass/ �µ� VulScanTaskAppServiceImpl.java��dispatch �߼���
3. project_backend/svmp/vul-pass/ �µ� VulScanTaskSubDomainServiceImpl.java��handlerVulProcess, writeVulInstLedger��
4. project_backend/svmp/vul-pass/ �µ� ITaskClient.java��Feign �� task-center��
5. project_backend/svmp/vul-pass/ �µ� VulScanTaskMapper.xml����ṹ�ο���

## ������
### 1. OpenTaskOrchestrator.java��domain �㣩
���ķ���: createOpenTask(req) �� { passTaskId, subTasks[] }
����:
  a. д vul_scan_task (biz_line=OPEN, data_origin=OPEN, scan_policy=SOC_DUAL, partner_id, external_task_id)
  b. �� scan_policy ���������:
     - SOC_DUAL: 2 �� sub (scanner_vendor=NESSUS + LM)
     - SINGLE: 1 �� sub
  c. ����� task-center first/half + second/half �·�
  d. д vul_scan_task_sub (external_survey_id, scanner_vendor, pass_task_id)
  e. ���� passTaskId + subTasks[]

### 2. OpenTaskUi.java��UI �㣩
- POST /internal/open/v1/tasks: ������������
  ������: { partnerId, platformTaskId, extTaskId, taskName, vulnType, targets, scanTemplateId?, reportTemplateId?, scanPolicy?, srcMethod?, callbackUrl? }
  ��Ӧ: { passTaskId, status, subTasks[], message? }
- GET /internal/open/v1/tasks/{passTaskId}: ��ѯ����
  ��Ӧ: { passTaskId, status, progress, subTasks[], finishedAt? }

### 3. ScanPolicyEnum.java
- SOC_DUAL: [NESSUS, LM]
- SINGLE: [�� type Ĭ��]
- CUSTOM: [����]

### 4. SubTaskStatusKafkaListener.java
- ���� SUB_TASK_STATUS_CHANGED
- ���� vul_scan_task_sub ״̬
- ���� sub FINISHED �� ���������ȡ + ����

### 5. ReportJobKafkaListener.java
- ���� REPORT_JOB_COMPLETED
- �� task-center download ��ȡԭʼ����
- �洢�� pass ������
- ����֪ͨ open-api

### 6. ITaskClient Feign ��չ
- GET /v1/scan/task/survey/{surveyId}/results
- POST /v1/scan/task/survey/{surveyId}/report/generate
- GET /v1/scan/report/jobs/{reportJobId}
- GET /v1/scan/report/jobs/{reportJobId}/download

### 7. VulResultMergeService.java�������ϲ���
- mergeUnion(rawNessus, rawLM) �� merged
- dedupKey = assetId + vulPort + vulTransProto + vulSvc + vulId
- ��ͻ: vulLevelȡ��, vulName/vulDescȡ�ǿ�, engHash��MULTI, transferTimeȡ����
- һ��ʧ��һ��ɹ�: �ɹ����������

### 8. ���������·
- ���� sub FINISHED �� �ֱ���ȡ results �� mergeUnion �� handlerReport �� handlerVulProcess
- handlerVulProcess: OPEN д oper �죨data_origin=OPEN������д report �죬���ش� order
- ��ɺ�� task-center report/generate
- ������ɺ�֪ͨ open-api (POST /internal/open/v1/tasks/{passTaskId}/notify)

## Լ��
- ���� ASSESS �� handlerReport / handlerVulProcess �����߼�
- biz_line ����: OPEN ֻд oper ��
- order_id �ɿգ�OPEN �޲���ָ�
- �ݵ�: external_task_id ȥ��

## ����
- [ ] POST /internal/open/v1/tasks ���������·� 2 �� survey
- [ ] Kafka ���� FINISHED �󴥷�����
- [ ] ����ȥ����ȷ
- [ ] ���Ȳ�ѯ���ؾۺ�״̬
- [ ] һ��ʧ��һ��ɹ����ɹ������
```

### Agent 3: open-api-service Adapter ��·

```text
���� open-api-service ��˿��� Agent��

## ����
�� open-api-service �� dispatch+��orderId ��Ϊ�� vul-pass internal API��

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md�����ߣ�
2. svmp/docs/internal/open-api-vtc-pass-��ط���.md�����壩
3. svmp/docs/external/���簲ȫ©������ƽ̨ �� API �ӿ��ĵ�.md����5.1 ��������

## �ض�����
1. project_backend/svmp/open-api-service/ �µ� SvmpEngineAdapterImpl.java�������������䣩
2. project_backend/svmp/open-api-service/ �µ� OpenTaskDomainServiceImpl.java
3. project_backend/svmp/open-api-service/ �µ� OpenTaskUi.java������ӿڣ�
4. project_backend/svmp/open-api-service/ �µ� open_task ��ṹ

## ������
### 1. �޸� SvmpEngineAdapterImpl
- �� POST /vul-scan-task/dispatch ��Ϊ POST /internal/open/v1/tasks
- ������ӳ��: extTaskId, taskName, vulnType(=type), targets, scanTemplateId, reportTemplateId, scanPolicy=SOC_DUAL, srcMethod, callbackUrl
- ��¼���ص� pass_task_id �� open_task

### 2. VulPassInternalClient.java��Feign��
- POST /internal/open/v1/tasks
- GET /internal/open/v1/tasks/{passTaskId}
- POST /internal/open/v1/tasks/{passTaskId}/notify���� vul-pass ���ã�

### 3. NotifyUi.java������ vul-pass ֪ͨ��
- POST /internal/open/v1/tasks/{passTaskId}/notify
- ������: { status, platformTaskId, summary?, errorMessage? }
- ���� open_task ״̬
- ���� Webhook TASK_COMPLETED / TASK_FAILED

### 4. ���Ȳ�ѯ��·
- GET /tasks/{taskId} �� �ڲ��� GET /internal/open/v1/tasks/{passTaskId}
- �ۺ�˫ɨ���ȷ���

### 5. WebhookService.java
- ���� TASK_COMPLETED / TASK_FAILED
- �����Ի���: ��� 5 �Σ�ָ���˱�
- Webhook ��ǩ: HMAC-SHA256

### 6. open_task �������ֶΣ�Liquibase��
- pass_task_id BIGINT
- scan_policy VARCHAR(32) DEFAULT 'SOC_DUAL'

## Լ��
- adapter-mode �����ã�mock/real���������׶οɲ���
- ���� API ��Լ���䣨��5.1��
- �ݵ�: extTaskId ȥ��

## ����
- [ ] Partner �������� �� open-api �� vul-pass ����
- [ ] ���Ȳ�ѯ����˫ɨ�ۺ�״̬
- [ ] vul-pass notify �� Webhook ����
- [ ] adapter-mode=mock �Կ���
```

### Agent 4: ǰ��������̨

```text
���� asset-newleak-manage ǰ�˿��� Agent��

## ����
���� OPEN ���������б� + ����ʵ������̨ҳ�档

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md����ʮ��
2. svmp/docs/internal/prototypes/open-api-vtc-pass-prototype-v1.html��ԭ�Ͳο���
3. .cursor/skills/esmp-frontend-dev/SKILL.md

## �ض�����
1. project_frontend/asset/asset-newleak-manage/src/router.config.js
2. project_frontend/asset/asset-newleak-manage/src/views/ �������б�ҳ�ο�
3. project_frontend/asset/asset-newleak-manage/src/api/ ������ API �ο�
4. asset-manage-master/src/views/demo/normal/���б�ҳ demo��

## ������
### 1. views/open-task/OpenTaskList.vue
- չʾ biz_line=OPEN �������б�
- ��: taskId, partnerId, taskName, scanPolicy, progress, status, ����(����̨)
- ʹ�� window.commonComponents.Search + AssetTable

### 2. views/open-task/OpenTaskWorkspace.vue
- Tab ���֣��ο�ԭ�ͣ�:
  1. ����: ʱ����չʾ����ȫ����
  2. ������(˫ɨ): ���ҶԱ� Nessus / ���˽�����©����
  3. �������: ���ӻ��������̣�չʾ dedupKey ���ͻ���
  4. ©����������: ʵ���б� + ״̬ԾǨ��ʷ
  5. �������: ԭʼ���� + ƽ̨��������
  6. Partner �ص�: Webhook Ͷ����־

### 3. components/DualScanPanel.vue
- ����˫�в���
- չʾ��ɨ�������ȡ�©������״̬
- ��ɫ��ʶ: RUNNING(��) / FINISHED(��) / FAILED(��)

### 4. components/MergeResultPanel.vue
- ���ӻ�����: [Nessus: 42] + [����: 38] �� [����: 51]
- չʾ dedupKey = �ʲ� + �˿� + Э�� + ���� + vulId
- ��ͻ�����ע

### 5. api/open-task.js
- getOpenTaskList(params)
- getOpenTaskDetail(passTaskId)
- getOpenTaskSubTasks(passTaskId)
- getOpenTaskVulnInstances(passTaskId)

### 6. router.config.js ·��ע��
- /open-task/list
- /open-task/workspace/:passTaskId

## Լ��
- Vue2 + Ant Design Vue
- ʹ�� window.commonComponents��Search, AssetBlock, AssetTable��
- ��Ӧ����������: mounted/unmount
- ���Ľ���

## ����
- [ ] �б�չʾ OPEN ����
- [ ] ����̨ 6 �� Tab ���л�
- [ ] ˫ɨ����ʵʱչʾ
- [ ] �������ӻ�����
```

---

## Wave 2 ִ�� Prompt

### Agent: vul-pass ASSESS ���� + task-center LM ������

```text
���� vul-pass + vuln-task-center ��˿��� Agent��

## ���������ֿɲ��У�

### Part A: vul-pass ASSESS dispatch ���� task-center �·�
�� project_backend/svmp/vul-pass �޸� VulScanTaskAppServiceImpl.dispatch:
- ���ӷ�֧: ASSESS ����Ҳ�� task-center first/half + second/half �·�
- д vul_scan_task_sub (external_survey_id)
- ���� report ���߼����䣨handlerVulProcess ��д rela_report + ̨�� + �ش� order��
- Kafka �������� W1 �� SubTaskStatusKafkaListener

### Part B: vuln-task-center ScannerAdapter-LM
�� project_backend/svmp/vuln-task-center ʵ��:
- ScannerAdapter �ӿ�
- LmScannerAdapter ʵ�֣���װ���� MsgSendLM �߼���
- ����ע���: scanner_vendor, scanner_api_capability �� + LM ��������
- scan_node ��չ: health_status, last_heartbeat_at, supported_capabilities, vendor_device_hash
- ��������: ReconcileDomainService + GET /v1/reconcile/tasks + POST /v1/reconcile/tasks/trigger
- LM ����Դ: GET /api/task/active_list
- ORPHAN/MISSING/DRIFT ����

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md������.4, ��ʮһ.2��
2. svmp/docs/internal/vuln-task-center-ɨ����������-PRD.md����5.1 VTC-GOV-P0��
3. svmp/docs/internal/©��ʵ������������˫��洢-��ط���.md�����ģ�

## �ض�����
1. vul-pass: VulScanTaskAppServiceImpl.java, VulScanTaskSubDomainServiceImpl.java
2. vuln-task-center: MsgSendLM.java, VulnTaskListenerLM.java, QueueAppServiceImpl.java

## Լ��
- ASSESS ���첻Ӱ�첿���ϱ���report �첻�䣩
- MsgSendLM ��ɾ����LM ���߼��� Adapter
- �������豸 API Ϊ׼
- Liquibase ���ظ�ִ��

## ����
- [ ] �������� task-center �·�
- [ ] ���˽ڵ���˷��� MATCHED/ORPHAN/MISSING/DRIFT
- [ ] ASSESS д report �죬OPEN д oper ��
- [ ] �����ѯ����Ӱ��
```

### Agent: vul-pass handlerVulProcess ����

```text
���� vul-pass ��˿��� Agent��

## ����
��� writeVulInstLedger Ϊ appendOperRela / appendReportRela���� biz_line ������

## �ض�����
1. project_backend/svmp/vul-pass/ �µ� VulScanTaskSubDomainServiceImpl.java
   - �ص�: writeVulInstLedger ����
   - �ص�: handlerVulProcess ����
2. project_backend/svmp/vul-pass/ �µ� vul_inst_log_rela ��ṹ

## ������
### 1. vul_inst_log_rela_oper ���Liquibase��
- �ֶμ� PRD ����.1.4
- ���� vul_inst_log_rela ������Ϊ report ��

### 2. appendOperRela ����
- д vul_inst_log_rela_oper
- data_origin �� inst һ��
- ledger_status=PENDING��̨�˺󲹣�
- synthesized=0

### 3. appendReportRela ����
- д vul_inst_log_rela���ֱ��� report �죩
- synthesized=0������ʵʱ��
- ̨��ͬ��

### 4. handlerVulProcess ����
- biz_line=ASSESS: appendReportRela��+ ��ѡ appendOperRela��+ ̨�� + �ش� order
- biz_line=OPEN: appendOperRela only������̨�˺ͻش�
- biz_line=METRIC: appendOperRela only������̨�˺ͻش�

## Լ��
- transition ״̬ԾǨ�߼�����
- �� rela д�����
- �����ѯ JOIN rela_report���ֱ������Ӱ��

## ����
- [ ] OPEN д oper ��
- [ ] ASSESS д report ��
- [ ] �����ѯ����
- [ ] mvn compile ͨ��
```

---

## Wave 3 ִ�� Prompt

### Agent: vul-pass + open-api ʵ���������� API

```text
���� vul-pass + open-api ��˿��� Agent��

## ����
ʵ��©��ʵ����֤/����/�޸�����ȫ�������� API��

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md����ˣ�
2. svmp/docs/external/���簲ȫ©������ƽ̨ �� API �ӿ��ĵ�.md����5.2-5.5��

## ������

### vul-pass ��
1. OpenInstanceUi.java: 6 �� internal �ӿ�
   - POST /internal/open/v1/instances/{vulInfoID}/verify
   - POST /internal/open/v1/instances/verify:batch
   - POST /internal/open/v1/instances/{vulInfoID}/remediate
   - POST /internal/open/v1/instances/remediate:batch
   - POST /internal/open/v1/instances/{vulInfoID}/verify-fix
   - POST /internal/open/v1/instances/verify-fix:batch

2. OpenInstanceAppServiceImpl: ҵ���߼�
   - verify: У��ǰ��״̬(0,1) �� transition �� 2/3 �� appendRela
   - remediate: У��ǰ��״̬(2,7) �� transition �� 5/9 �� appendRela
   - verify-fix: У��ǰ��״̬(5) �� �첽��ɨ �� ��ɺ� 6/7/10 �� Webhook

3. verify-fix 异步复扫（§5.5 全链路）
   - Partner 发起；同步返回 verifyFixJobId，受理期间保持 stat=5
   - 按 vulInfoID 加载 vul_archive_inst，从系统漏洞库取影响资产 IP -> targets
   - 查询实例最近一次扫描 sub.scanner_vendor（单厂商，非 SOC_DUAL）
   - 调 task-center 下发**全量扫描**（不支持指定产品漏洞 ID）
   - Kafka 回收全量结果；**仅匹配** verify-fix 目标 vulInfoID 判定：
     未再检出->6（核验修复），仍检出->7（核验未修复），失败/超时->10
   - notify open-api -> INSTANCE_VERIFY_FIX_COMPLETED + EXPORT_READY(VERIFY_FIX_SCAN)

### open-api ��
4. InstanceUi.java: 8 ������ӿڣ���5.2-5.5��
5. InstanceAppServiceImpl: Feign �� vul-pass + DTO ת��
6. �ݵ�: Idempotency-Key ���� 24h
7. open_vuln_instance ӳ��

## ״̬Լ��
- verify: ǰ�� 0,1 �� 2(VALID) �� 3(FALSE_POSITIVE, ��̬)
- remediate: ǰ�� 2,7 �� 5(���޸�) �� 9(�޸�ʧ��/����)
- verify-fix: ǰ�� 5 �� 6/7/10

## ����
- [ ] verify ״̬ԾǨ��ȷ
- [ ] remediate ���޸�/������֧��ȷ
- [ ] verify-fix �첽��ɨ���
- [ ] �ݵȼ���Ч
- [ ] �����ӿڲ��ֳɹ�
```

---

## Wave 4 ִ�� Prompt

### Agent: open-api Export/Artifact + vul-pass METRIC Ǩ��

```text
���� open-api + vul-pass ��˿��� Agent��

## ���������֣�

### Part A: Export/Artifact �ⷢ
1. vul-pass TaskExportAssembler: ��װ TaskExport XML/JSON
   - �ṹ: export/task/summary/targets/liveProbeResults/portScanResults/vulnerabilities/weakPasswords/baselineResults/appendices
   - SOC_DUAL �ۺϺ�ͳһ���
   - ����������
2. open-api ExportUi: /exports/* �ӿ�
3. open-api ArtifactUi: /artifacts/* �ӿ�
4. open_export / open_artifact ��
5. Webhook EXPORT_READY / ARTIFACT_READY

### Part B: METRIC Ǩ��
1. vul-pass MetricTaskUi: /ui/pass/v3/metric/*
2. MetricTaskOrchestrator: biz_line=METRIC ����
3. handlerVulProcess biz_line=METRIC ��֧��д oper �죩
4. Ǩ�ƽű�: vuln_sys �� vul_archive_inst (data_origin=METRIC)
5. Ǩ�ƽű�: vuln_sys_history �� vul_inst_log_rela_oper

## �ض��ĵ�
1. svmp/docs/internal/SOC�Խ�ȫ��·-PRD.md����ţ�
2. svmp/docs/external/���簲ȫ©������ƽ̨ �� API �ӿ��ĵ�.md����5.6-5.7, ��7��
3. svmp/docs/internal/vuln-modelɨ�������ع�Ǩ����vul-pass-��ط���.md��ȫ�ģ�

## ����
- [ ] Export XML/JSON ������
- [ ] Artifact ԭʼ���������
- [ ] Webhook ֪ͨ����
- [ ] METRIC ������ vul-pass �����
- [ ] ��ʷ©��Ǩ���� inst + oper ��
```

---

## ִ������

```text
1. �û��ظ���ͬ��ִ�С�
2. auto-dev-orchestrator ��ȡ���ļ� + task-matrix.yaml
3. �� Wave ˳��ִ��:
   W1: 4 �� Agent ���У�VTC-API, PASS-ORCH, OAS-ADAPTER, FE-WORKSPACE��
   W2: 2 �� Agent ���У�PASS-ASSESS+VTC-LM, PASS-RELASPLIT��
   W3: 1 �� Agent��PASS+OAS-INSTANCE��+ 1 �� Agent��FE-INSTANCE��
   W4: 1 �� Agent��PASS+OAS-EXPORT��+ 1 �� Agent��PASS-METRIC��+ 1 �� Agent��FE-EXPORT��
4. ÿ�� Wave ��ɺ� Review ����
5. ȫ����ɺ�ժҪ����
```


---

## 代码分析修正（v1.1）

> 基于四工程深度代码分析，以下 Prompt 内容需修正：

### Agent 3 修正：open-api Adapter 改路

原 Prompt 说"新建 VulPassInternalClient Feign"，实际应修正为：

1. **修改现有 IVulPassScanTaskFeign**（已存在于 infra/feign/IVulPassScanTaskFeign.java）
   - 从 @PostMapping("/vul-scan-task/dispatch") 改为 @PostMapping("/internal/open/v1/tasks")
   - 从 @GetMapping("/vul-scan-task/page2") 改为 @GetMapping("/internal/open/v1/tasks/{passTaskId}")

2. **修改 SvmpEngineAdapterImpl**（已存在于 infra/adapter/SvmpEngineAdapterImpl.java）
   - 翻译层从 dispatch 请求改为 internal open API 请求
   - 删除假 orderId 逻辑（格式 1-31-19位数字）

3. **open_task 表无需新增 DDL**
   - pass_task_id、scan_policy 字段已存在

4. **Webhook 直接复用**
   - WebhookDomainServiceImpl 已实现 HMAC-SHA256 验签 + 重试3次
   - 仅需在 notify 接收后触发 publishTaskCompleted

5. **幂等直接复用**
   - extTaskId 业务幂等（partner_task_map）已实现
   - IdempotencyInterceptor（24h Redis）已实现

### Agent 2 修正：vul-pass OpenTaskOrchestrator

原 Prompt 说"复用 ITaskClient"，实际应修正为：

1. **新建 ITaskClient Feign**（当前不存在）
   - 调用 task-center: first/half、second/half、results、report API
   - 放在 infra/feign/ITaskClient.java

2. **Kafka 监听复用现有 topic**
   - 监听 dr_vul_scan_task_status topic（已存在）
   - 消息体需增加 passTaskId、passSubTaskId 字段（由 task-center 下发时透传）

3. **biz_line/data_origin 字段已存在于 PO/DO**
   - OpenTaskOrchestrator 创建任务时主动赋值即可
   - 无需新增 DDL

### Agent 1 修正：vuln-task-center API

1. **Kafka 生产者复用现有 topic**
   - dr_vul_scan_task_status 已被 VulnTaskListenerOther.sendKafkaToInformLifecycle 使用
   - 修正：在该消息体中增加 passTaskId、passSubTaskId 字段
   - 由 QueueAppServiceImpl.send() 下发时从请求参数透传

2. **scan_sub_task 表已存在**
   - 已有 surveyId/planId/state/sendParamsInfo 字段
   - 需新增 pass_task_id、pass_sub_task_id 字段（Liquibase）

### W4 修正：open-api Export

1. **open_export/open_export_file 表已存在**
2. **ExportAssemblyDomainServiceImpl 组装管道已实现**
3. **MockTaskExportAssembler 已实现组装逻辑**
4. W4 动作：将 MockTaskExportAssembler 的数据源从 Mock 切换为真实 vul-pass 拉取的数据
5. 补充 Webhook 事件类型：ARTIFACT_READY、INSTANCE_VERIFY_FIX_COMPLETED

# ============================================================
# 双阶段交叉扫描 Multi-Agent 执行 Prompt（2026-06-17 追加）
# 方案文档: svmp/docs/internal/双阶段交叉扫描方案-SOC并集与部侧交集统一.md
# ============================================================

## Agent: W1b-PASS-ORCH（vul-pass 双阶段扫描编排）

```
你是 ESMP 后端开发 Agent，负责 vul-pass 双阶段扫描编排实现。

## 背景
SOC 接入要求每次任务下发到 Nessus 和绿盟扫描器，结果取并集。
部侧考核要求交叉扫描验证取交集。
为规避特殊定制，采用双阶段模型：排查阶段单扫描器，验证阶段多扫描器 + 可配置合并策略。

## 必读文档
1. d:\application\solo\3.0\svmp\docs\internal\双阶段交叉扫描方案-SOC并集与部侧交集统一.md
2. d:\application\solo\3.0\.cursor\rules\backend-framework-context.mdc
3. d:\application\solo\3.0\.cursor\skills\esmp-backend-dev\SKILL.md
4. d:\application\solo\3.0\.cursor\skills\esmp-rd-standards\SKILL.md

## 现有代码基础（务必复用，不修改 transition 规则）
- VulProcessMethodEnum.CROSS_SCAN_VERIFICATION (1026) - 交叉扫描验证处置方式
- TransitionEnum PHASE_VALIDATION 规则 - EXISTENT→3, STILL_EXIST→2
- VulCrossVerifyParser - 交叉扫描结果解析器
- CommonUtil.buildVulInfoLstByEngHashMap - 多设备结果合并（procMethod=1026 分支）

## 任务范围
1. 新增 VerifyMergeStrategy 枚举（UNION / INTERSECT）
2. OpenTaskOrchestrator.triggerVerificationPhase 方法
   - 排查阶段完成后自动触发验证阶段（biz_line=OPEN 场景）
   - 创建验证阶段任务：tsk_phase=2, proc_method=1026
   - 按 verify_scanner_vendors 创建多个子任务
   - 加载排查阶段发现的漏洞实例作为验证目标
3. Liquibase DDL：
   - vul_scan_task 新增 verify_merge_strategy VARCHAR(16) DEFAULT 'INTERSECT'
   - vul_scan_task 新增 verify_scanner_vendors VARCHAR(256)
   - vul_scan_task_sub 新增 scan_phase TINYINT DEFAULT 1
   - vul_scan_task_sub 新增 verify_round INT

## 禁止
- 修改 TransitionEnum 任何规则
- 修改 handlerVulProcess 核心逻辑
- 修改 VulCrossVerifyParser

## 验收
- 排查阶段任务完成后，biz_line=OPEN 自动触发验证阶段
- 验证阶段任务 procMethod=1026, tskPhase=2
- 验证阶段按 verify_scanner_vendors 创建多个子任务
- Partner 可配置是否自动触发验证阶段

## 执行步骤
1. 阅读 d:\application\solo\3.0\svmp\docs\internal\双阶段交叉扫描方案-SOC并集与部侧交集统一.md
2. Grep 定位 vul-pass 现有 CROSS_SCAN_VERIFICATION 相关代码
3. 按 DDD 四层结构实现，参考 esmp-starter-task
4. 编写 Liquibase 脚本
5. 自测 triggerVerificationPhase 逻辑
```

## Agent: W1b-PASS-MERGE（vul-pass 验证结果合并器）

```
你是 ESMP 后端开发 Agent，负责 vul-pass 验证结果合并器实现。

## 背景
双阶段扫描的验证阶段需要合并多扫描器结果。
SOC 接入取并集（UNION），部侧考核取交集（INTERSECT）。

## 必读文档
1. d:\application\solo\3.0\svmp\docs\internal\双阶段交叉扫描方案-SOC并集与部侧交集统一.md
2. d:\application\solo\3.0\.cursor\rules\backend-framework-context.mdc
3. d:\application\solo\3.0\.cursor\skills\esmp-backend-dev\SKILL.md

## 任务范围
1. VerifyResultMerger.java
   - mergeVerifyResults(List<List<VulScanTaskSubResultDO>>, VerifyMergeStrategy, dedupKeyFunction)
   - UNION: 所有扫描器结果的 key 取并集
   - INTERSECT: 所有扫描器都发现的 key 取交集
   - 单扫描器场景直接返回
2. mergeConflict 方法（并集模式冲突解决）
   - vulLevel 取高
   - vulName / vulDesc 取非空
   - engHash 记 "MULTI"
   - evidenceSources 记录所有来源
   - transferTime 取最早
3. dedupKey 函数
   - = assetId + vulPort + vulTransProto + vulSvc + vulId
   - 与 vul_archive_inst 唯一键一致
4. 单元测试 VerifyResultMergerTest
   - UNION 场景：两边都发现 / 仅A发现 / 仅B发现 / 两边都未发现
   - INTERSECT 场景：同上
   - 单扫描器场景
   - 冲突合并场景

## 禁止
- 修改 transition 规则
- 修改 vul_archive_inst 唯一键定义

## 验收
- UNION: 任一扫描器发现即保留
- INTERSECT: 所有扫描器都发现才保留
- 冲突字段合并策略正确
- 单元测试覆盖率 > 90%

## 执行步骤
1. 阅读双阶段交叉扫描方案文档 §四.1-四.3
2. Grep 定位 vul_archive_inst 唯一键定义（Constant.concat）
3. 实现 VerifyResultMerger
4. 编写单元测试
5. 运行测试验证
```

## Agent: W1b-PASS-VERIFY（vul-pass 验证阶段 Kafka 监听与生命周期衔接）

```
你是 ESMP 后端开发 Agent，负责 vul-pass 验证阶段结果回收与生命周期衔接。

## 背景
验证阶段多扫描器子任务完成后，需要合并结果并执行 transition 状态跃迁。
关键：复用现有 handlerVulProcess，不修改 transition 规则。

## 必读文档
1. d:\application\solo\3.0\svmp\docs\internal\双阶段交叉扫描方案-SOC并集与部侧交集统一.md
2. d:\application\solo\3.0\svmp\docs\internal\漏洞实例与生命周期双轨存储-落地方案.md
3. d:\application\solo\3.0\.cursor\rules\backend-framework-context.mdc
4. d:\application\solo\3.0\.cursor\skills\esmp-backend-dev\SKILL.md

## 现有代码基础（务必复用）
- VulScanTaskSubDomainServiceImpl.handlerVulProcess - 漏洞生命周期处理
- VulScanTaskSubDomainServiceImpl.writeVulInstLedger - 台账日志写入
- TransitionEnum - 状态跃迁规则（不修改）
- IVulServiceClient - vuln-service Feign client

## 任务范围
1. 扩展 SubTaskStatusKafkaListener
   - 监听 dr_vul_scan_task_status topic
   - scan_phase=2 时进入验证阶段处理分支
   - 所有验证子任务完成后触发合并
2. 验证阶段结果回收流程
   - 拉取各扫描器 survey 结果（调 task-center API）
   - 调用 VerifyResultMerger.mergeVerifyResults 合并
   - 调用 handlerVulProcess 执行 transition
   - transition 结果：
     * 合并结果 ∩ 档案库 ≠ ∅ → STILL_EXIST → VALIDATED_TRUE(2)
     * 合并结果 ∩ 档案库 = ∅ → EXISTENT → VALIDATED_FALSE(3)
   - 验证阶段新发现（NEW_DISCOVERY）单独标记为 INITIAL_DISCOVERY(1)
3. 通知 open-api-service
   - POST /internal/open/v1/tasks/{passTaskId}/notify
   - summary: { totalInstances, verifiedValid, falsePositive, newDiscovery }

## 禁止
- 修改 TransitionEnum 任何规则
- 修改 handlerVulProcess 核心逻辑
- 修改 writeVulInstLedger 台账写入逻辑

## 验收
- 验证阶段所有子任务完成后触发合并
- 合并结果与档案库 diff，执行 transition
- VALIDATED_TRUE(2) / VALIDATED_FALSE(3) 状态正确
- 验证阶段新发现单独标记
- 通知 open-api-service 含完整 summary

## 执行步骤
1. 阅读双阶段交叉扫描方案文档 §四.5
2. Grep 定位 SubTaskStatusKafkaListener 现有实现
3. Grep 定位 handlerVulProcess 调用方式
4. 扩展 Kafka 监听，增加 scan_phase=2 分支
5. 实现验证阶段结果回收流程
6. 自测完整流程
```

# ============================================================
# v2 修订 Multi-Agent 执行 Prompt（2026-06-17 追加）
# auto_verify 参数 + 推迟 Webhook 回调
# 方案文档: svmp/docs/internal/SOC对接全链路-PRD-v2修订附录.md
# ============================================================

## Agent: W1b-OPEN-AUTOVERIFY（open-api-service 创建任务新增 auto_verify 参数）

```
你是 ESMP 后端开发 Agent，负责 open-api-service 创建任务接口新增 auto_verify 参数。

## 背景
SOC 接入要求创建任务后自动触发双扫描器验证阶段。
通过 autoVerify 参数控制：true（默认）时排查完成后自动触发验证，全部完成后统一回调；false 时排查完成即回调（原语义）。
此方案用「推迟回调」替代「新增事件」，API 改动最小化。

## 必读文档
1. d:\application\solo\3.0\svmp\docs\internal\SOC对接全链路-PRD-v2修订附录.md（§二 创建任务接口修订）
2. d:\application\solo\3.0\svmp\docs\internal\双阶段交叉扫描方案-SOC并集与部侧交集统一.md
3. d:\application\solo\3.0\.cursor\rules\backend-framework-context.mdc
4. d:\application\solo\3.0\.cursor\skills\esmp-backend-dev\SKILL.md
5. d:\application\solo\3.0\.cursor\skills\esmp-rd-standards\SKILL.md

## 现有代码基础
- OpenTaskUI.java: 创建任务接口（POST /tasks/vul 请求体新增 autoVerify 参数；POST /tasks/file 通过附录 G.2 XML 路径配置）
- OpenTaskDomainServiceImpl.java: 任务创建核心逻辑
- SvmpEngineAdapterImpl.java: open-api 与 vul-pass 的适配层
- IVulPassScanTaskFeign.java: 调用 vul-pass 的 Feign client
- OpenTaskDO.java / open_task PO: 任务实体

## 任务范围
1. POST /tasks/vul 请求体新增 autoVerify 参数（boolean, 可选, 默认 true）
2. XML 创建任务（POST /tasks/file）不新增请求体参数行，autoVerify 通过附录 G.2 的 XML 路径 /scanTask/server/autoVerify 配置
3. OpenTaskDO 新增 auto_verify 字段
4. open_task 表新增 auto_verify 字段（Liquibase，TINYINT(1) DEFAULT 1）
5. SvmpEngineAdapterImpl 传递 auto_verify 给 vul-pass
6. IVulPassScanTaskFeign 内部接口新增 auto_verify 参数
7. Partner 级配置可覆盖默认 auto_verify 值

## 关键约束
- autoVerify 默认 true（符合 SOC 需求）
- Partner 级配置 defaultAutoVerify 可覆盖请求体缺省值
- 请求体显式传值优先于 Partner 级配置
- auto_verify 传递到 vul_scan_task.auto_verify 字段

## 验收
- POST /tasks/vul 请求体支持 autoVerify，默认 true
- POST /tasks/file 通过附录 G.2 XML 路径 /scanTask/server/autoVerify 配置 autoVerify
- open_task 表 auto_verify 字段正确持久化
- auto_verify 传递到 vul-pass 的 vul_scan_task
- Partner 级配置可设置默认 auto_verify

## 执行步骤
1. 阅读SOC对接全链路-PRD-v2修订附录.md §二
2. Grep 定位 OpenTaskUI 创建任务接口
3. Grep 定位 OpenTaskDO 和 open_task PO
4. 新增 autoVerify 参数和字段
5. 编写 Liquibase 脚本
6. 修改 SvmpEngineAdapterImpl 和 IVulPassScanTaskFeign 传递参数
7. 实现 Partner 级配置覆盖逻辑
8. 自测参数传递链路
```

## Agent: W1b-OPEN-DEFERRED-CALLBACK（open-api-service 推迟回调控制）

```
你是 ESMP 后端开发 Agent，负责 open-api-service 推迟回调机制实现。

## 背景
auto_verify=true 时，排查阶段完成后不触发 TASK_COMPLETED 和 EXPORT_READY；
验证阶段完成（或任一阶段失败）时统一触发回调。
回调的实例状态反映验证后终态（2/3/1）。
此方案用「推迟回调」替代「新增 Webhook 事件」，不新增 INSTANCE_AUTO_VERIFIED。

## 必读文档
1. d:\application\solo\3.0\svmp\docs\internal\SOC对接全链路-PRD-v2修订附录.md（§三 状态流转、§四 Webhook 回调时机、§五 数据外发）
2. d:\application\solo\3.0\svmp\docs\internal\双阶段交叉扫描方案-SOC并集与部侧交集统一.md
3. d:\application\solo\3.0\.cursor\rules\backend-framework-context.mdc
4. d:\application\solo\3.0\.cursor\skills\esmp-backend-dev\SKILL.md

## 现有代码基础
- WebhookDomainServiceImpl.java: Webhook 发布逻辑
- WebhookEventType.java: 事件类型枚举
- OpenTaskDomainServiceImpl.java: get 方法（合并引擎进度、触发实例入库和通知）
- IVulPassScanTaskFeign.java: 调用 vul-pass 获取任务状态和实例
- ExportService: 外发服务

## 任务范围
1. PassTaskStatusListener（新建或扩展）
   - 监听 vul-pass 任务状态变更（通过 Kafka 或 Feign 轮询）
   - 按 tsk_phase 和 auto_verify 控制回调时机
2. 回调时机控制逻辑
   - auto_verify=true:
     * tsk_phase=1 FINISHED → 不回调，等待验证阶段
     * tsk_phase=2 FINISHED → 统一回调 TASK_COMPLETED + EXPORT_READY
     * 任一阶段 FAILED → 回调 TASK_FAILED
   - auto_verify=false:
     * tsk_phase=1 FINISHED → 回调 TASK_COMPLETED + EXPORT_READY（原语义）
3. EXPORT_READY 外发内容（auto_verify=true 时）
   - 包含排查+验证两阶段合并结果
   - vulnerabilities[].instances[].vulInfoStat 反映验证后终态
   - summary 含 verifiedValid / falsePositive / initialDiscovery 统计
4. TASK_COMPLETED payload（auto_verify=true 时）
   - summary 反映验证后终态统计
5. 单元测试
   - auto_verify=true: 排查完成不回调
   - auto_verify=true: 验证完成统一回调
   - auto_verify=false: 排查完成即回调
   - 任一阶段失败: 回调 TASK_FAILED

## 关键约束
- 不新增 Webhook 事件类型（保持原有 6 个事件）
- 不新增 verify_source 字段
- 回调的 instances[].vulInfoStat 必须反映验证后终态
- EXPORT_READY 外发须含两阶段合并结果

## 验收
- auto_verify=true：排查完成不回调 TASK_COMPLETED
- auto_verify=true：验证完成统一回调 TASK_COMPLETED，payload summary 反映终态
- auto_verify=true：EXPORT_READY 在验证完成后触发，含两阶段合并结果
- auto_verify=false：排查完成即回调（原语义不变）
- 任一阶段失败：回调 TASK_FAILED
- 回调的 instances[].vulInfoStat 反映验证后终态（2/3/1）

## 执行步骤
1. 阅读SOC对接全链路-PRD-v2修订附录.md §三/§四/§五
2. Grep 定位 WebhookDomainServiceImpl 和 WebhookEventType
3. Grep 定位 OpenTaskDomainServiceImpl 的 get 方法
4. 实现 PassTaskStatusListener（或扩展现有监听器）
5. 实现按 tsk_phase 和 auto_verify 的回调时机控制
6. 实现 EXPORT_READY 两阶段合并外发内容
7. 编写单元测试
8. 自测完整流程
```

## v2 修订对 W1b-PASS-VERIFY 任务的补充说明

原 W1b-PASS-VERIFY 任务（vul-pass 验证阶段 Kafka 监听与生命周期衔接）需追加以下要求：

```
## v2 补充要求（W1b-PASS-VERIFY）

验证阶段完成后通知 open-api-service 时，必须携带 tsk_phase=2 标识，
供 open-api-service 的推迟回调机制判断回调时机。

通知 payload 示例：
{
  "passTaskId": "...",
  "tskPhase": 2,
  "status": "FINISHED",
  "summary": {
    "totalInstances": 3,
    "verifiedValid": 2,
    "falsePositive": 1,
    "initialDiscovery": 0
  }
}

关键：
- tsk_phase=1 FINISHED 通知：排查阶段完成（open-api 据此判断是否等待验证阶段）
- tsk_phase=2 FINISHED 通知：验证阶段完成（open-api 据此触发统一回调）
- 任一阶段 FAILED 通知：失败回调
```