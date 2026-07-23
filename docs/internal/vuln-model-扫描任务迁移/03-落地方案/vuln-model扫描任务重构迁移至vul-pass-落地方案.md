# vuln-model ɨ���������Ĺ��� �� vul-pass �ع�Ǩ�� �� ��ط���

> **״̬**���ݰ� v0.2�������� �� �ع� + һ���Ը�ӣ�  
> **����**��2026-06-14  
> **����**��vul-pass / vuln-model ��ˡ���ά����Ʒ����ǰ��  
> **�����ĵ�**��[©��ʵ������������˫��洢-��ط���](./©��ʵ������������˫��洢-��ط���.md) �� [Open API �� vul-pass �ڲ��ӿ�ӳ���](./Open%20API��vul-pass�ڲ��ӿ�ӳ���.md)

---

## һ��Ǩ�����ʣ���ȷ�ϣ�

| ������ | ���� |
|--------|------|
| Ǩ�Ʒ�ʽ | **������ȫ�ع�**���ǽӿڰ�ҡ��ǽ������� |
| ������ | �ع����ǰ **vuln-model ����������Ӫ**���� pass �ع�����Ӱ�� |
| ��ӷ�ʽ | �ع�����ͨ���� **һ��������Ǩ�ƣ�Big Bang��**��Ȼ������ vuln-model ɨ�������� |
| ǰ�� | **ǰ���ͬ������**����˿�������� REST ��Լ��**�����Ǿ� API ����** |
| ��ʷ©�� | **ȫ��Ǩ�� `rela_oper`**����ȷ�ϣ���inst ����ȫ��ӳ���� `vul_archive_inst` |
| ˫����� | �ع��ڽ� `data_origin=METRIC` + oper �죻�ϱ�����ѡ�ϳ� report �죨��˫�췽�� ��4.3�� |

---

## ����Ŀ��ܹ�

### 2.1 �����ڣ��ع������׶Σ�

```text
vuln-model��������Ӫ��
  VulScanTaskUi �� vul_scan_task* (model��) �� vuln_sys / vuln_sys_history
              �� ���� XLSX �� vul-pass recycle�����ɣ����ǰ�Կ��ã�

vul-pass���ع�������
  ui/pass/v3/metric/* �� MetricTaskOrchestrator
                    �� recycle / handlerVulProcess (biz_line=METRIC)
                    �� vul_archive_inst (data_origin=METRIC)
                    �� vul_inst_log_rela_oper���ճ�ֻд oper��
```

### 2.2 ��Ӻ�

```text
��ǰ�� �� vul-pass metric API
              �� inst + rela_oper����ʵ�켣��
              �� ÿ����ѡ + �ϳ� rela_report �� ��̬���ϱ�

vuln-model ɨ�������� �� ���ߣ���ֻ���鵵��
```

---

## �����ع���Χ

### 3.1 In Scope�������� pass �ؽ���

�� vuln-model `VulScanTaskUi` ����������Ϊ**������**��ʵ��ʱ���󶨾� URL��

| ҵ���� | vuln-model �ο� | pass �ع���� |
|--------|-----------------|---------------|
| ������� | `/batch`��`/start` | `MetricTaskOrchestrator`��engHash ɨ��������� task-center�� |
| �����ѯ | `/query`��`/index/primary` | `MetricTaskQueryAppService`��`data_origin=METRIC` ���� |
| ɨ���� | `/repeatScan`��`/change/offline/status`��`/handle` | ��չ `recycle/preview` + METRIC ���� |
| ��͸���� | `/batch/import`��`/changeTaskStatus` | `procMethod=109` + oper ��״̬�� |
| ����ʵ�� | `VulScanTaskInstanceUi` | `VulScanTaskSub*` ��ϵ��չ |
| ���񸽼� | `VulScanTaskFileUi` | pass ���񸽼����� |
| ͳ��/TTL | `VulScanTaskStatUi`��`VulScanTaskTtlUi` | pass �� Scheduler |
| ���˱��� | `/reporting`��`/reporting/export` | `MetricAuditAppService`������Դ `inst`+`rela_oper` |
| �������� | `VulSysLifeCycleExecutor` | **����**���� `handlerVulProcess` + oper ����� |
| ���ݳ��� | `/export` �� XLSX ϴ�� | **��Ӻ����** |

### 3.2 Out of Scope�����׶β�Ǩ��

| ģ�� | ˵�� |
|------|------|
| `VulRecord*` ������ϵ | ������Ŀ |
| vuln-model `vuln_sys` ���ṹ���� | ���ʱӳ�䵽 `vul_archive_inst`��������ƽ�б� |
| �� REST ·������ | ��ǰ�˶Խ�����Լ |
| vuln-task-center �������� | Wave 4 �Ͽ����ع����� engHash |

### 3.3 ������ṹ��vul-pass��

```text
ui/pass/v3/metric/              # METRIC ר�� REST���� ASSESS �� VulScanTaskUi ���룩
app/service/metric/           # Orchestrator / Query / Audit
domain/pass/metric/             # ���������������
infra/metric/                   # engHash ����
infra/migration/                # һ���Ը�ӽű���Phase 3~4��
```

---

## �ġ����ڼƻ�

### Phase 0 �� ���󶳽��������̵㣨2 �ܣ�

��˫�췽�� Wave 0 ���С�

| ���� | ˵�� |
|------|------|
| ���� parity �嵥 | ���� ��3.1 |
| �ֶ�ӳ��� | ��¼ A��inst������¼ B��rela_oper������¼ C��״̬�룩 |
| ����ָ�� | ��¼ D |
| ˫�� Schema ���� | `rela_oper`��`data_origin`��`biz_line` |

**vuln-model**����Ķ���������Ӫ��

---

### Phase 1 �� ������ʩ����˫�� Wave 1 ͬ����

| ���� |
|------|
| Liquibase������ `vul_inst_log_rela_oper`���� `vul_inst_log_rela` �ݽ�Ϊ report �ṹ |
| `vul_archive_inst` ���� `data_origin`��`reportable_flag` |
| `vul_scan_task` ���� `biz_line`��`data_origin`��`metric_task_id`��`tsk_scn` |
| `handlerVulProcess` ������`METRIC` �� ֻд oper |
| `writeVulInstLedger` ���Ϊ `appendOperRela` / `appendReportRela` |
| �� REST ��Լ�ĵ�������ǰ�ˣ� |

---

### Phase 2 �� �����ع������Ŀ����ڣ�

**����˳��**��

1. ���� CRUD + ��ѯ����Ȩ�ޣ�  
2. ɨ������ + recycle �������  
3. ��͸���� + oper ��״̬��ת  
4. ��ɨ / ���� / �Զ�ͬ��  
5. ���˱���  
6. �������Ӻ��������ѡ����̨�Խ�˫�� Wave 3  

**����**�����Ի�����ǰ�� + �� pass API **�ջ�**�������� vuln-model��

**vuln-model**��������Ӫ��

---

### Phase 3 �� ������Ǩ������

| ���� |
|------|
| ��3.1 parity ��������� |
| ����Ǩ�ƽű����� + **��2 �� dry-run**���������գ� |
| ���˱����Զ�������¼ D�� |
| �ع�Ԥ�������ʧ�ָܻ� model д�� |

---

### Phase 4 �� һ���Ը�ӣ�Big Bang��

```text
T0  ά�����ڿ�ʼ
T1  ���� vuln-model д������ֻ����
T2  ȫ������Ǩ�ƣ����塢��¼ A~C��
T3  �Զ������� + �˹����
T4  ��ǰ�� + �� pass API ����
T5  vuln-model ɨ�������������
T6  ���Ŷ�д����� 72h
```

**��Ӻ������ϱ�**������Ǩ��� oper ������ִ��һ�Ρ���ѡ + �ϳ� report + ��̨�ˡ������ĩ�� Excel ���롣

---

## �塢һ��������Ǩ�Ʋ��ԣ���ȷ�ϣ�ȫ�� oper��

### 5.1 Ǩ��ԭ��

| ԭ�� | ˵�� |
|------|------|
| ȫ����ʷ | **����**�ڲ�����©��Ǩ�� `vul_archive_inst` + `rela_oper` |
| ֻд oper | Ǩ������ `synthesized=0`����ʵ��ʷ����`ledger_status=PENDING` |
| ��д report | report ���ɸ�Ӻ���ѡ�ϳɲ�����Ǩ�ƽű�**��д** report |
| �ݵ� | �ű����ظ� dry-run������ӳ���ȥ�� |
| ID ӳ�� | ���뱣�� `model_vuln_sys_id �� pass_inst_id` ӳ��� |

### 5.2 Ǩ������˳��

```text
Batch 1  vul_scan_task* Ԫ����        �� pass vul_scan_task* (biz_line=METRIC)
Batch 2  vuln_sys ��ǰ����            �� vul_archive_inst (data_origin=METRIC)
Batch 3  vuln_sys_history ȫ���켣    �� rela_oper���� update_time ����׷�ӣ�
Batch 4  ����-ʵ������������          �� pass ������/������
Batch 5  ���˱���                     �� ���� CSV
```

### 5.3 Ǩ�ƺ�Ǩ / ֻ���鵵

| ���� | ���� |
|------|------|
| model Kafka offset��TTL ���� | ��Ǩ |
| task-center �ⲿ���� | `metric_task_id` ���飬������ |
| ���ǰδ������ XLSX | ���ǰ�˹�������� |

---

## ���������嵥����Ӻ�

| ��� | ���� |
|------|------|
| `com.mvtech...vuln.ui.VulScanTaskUi` �� metric �� Ui | �������� |
| `VulScanTaskAppServiceImpl`��`VulSysLifeCycleExecutor` | ���� deprecated |
| `ITaskClient`��vuln-task-center�� | �Ͽ� |
| model `vuln_sys` д·�� | ���ߣ���ֻ���鵵 ��6 �� |
| model �� pass XLSX ����������·�� | ���� |

---

## �ߡ�������Բ�

| ���� | �Բ� |
|------|------|
| `vuln_sys.status` �� `vulInfoStat` �����һ�� | ��¼ C ӳ��� + δӳ�����˹����� + dry-run ���챨�� |
| ��ʷ�� `vuln_sys_history` ��ʵ�� | �� `vuln_sys` ��ǰ״̬�ϳ�һ�� oper ��¼ |
| �ʲ� ID ��ϵ��ͬ��model target vs pass assetId�� | ���ǰ�ʲ�ӳ������޷�ӳ��ı�� `assetLclId` |
| Ǩ�ƴ��ڳ�ʱ | ����д�⣻Batch ���У�Ԥ��ѹ������ |
| ˫�� Schema δ����͸�� | Phase 1 Ϊ Phase 4 Ӳ���� |

---

## �ˡ������־

| �汾 | ���� | ˵�� |
|------|------|------|
| 0.1 | 2026-06-14 | ���壺�����л��棨�ѷ�ֹ�� |
| 0.2 | 2026-06-14 | �޶����ع� + Big Bang��ȷ����ʷȫ��Ǩ oper��ǰ���ͬ������ |

---

## ��¼ A��`vuln_sys` �� `vul_archive_inst` �ֶ�ӳ��

> ��ӽű� Batch 2 ʹ�á�`pass_inst_id` �����ɣ�ѩ��/������򣩣�ӳ�����¼ `model_id �� pass_id`��

| vuln-model `vuln_sys` | pass `vul_archive_inst` | ת������ |
|------------------------|-------------------------|----------|
| `id` (UUID) | `id` | **������**���� ID ���� `migration_id_map` |
| `vulId` | `vulId` | ֱ�� |
| `name` | `vulName` | ֱ�� |
| `cveId` | `orgVulId` | ֱ�� |
| `level` | `vulLevel` | �ȼ���ӳ�䣨����Ʒȷ�Ͼ������ |
| `status` | `vulInfoStat` | ����¼ C |
| `target` | `vulNetAddr` | ֱ����URL �ͱ��� |
| `port` | `vulPort` | ת Integer����Ч�� null |
| `protocol` | `vulTransProto` | ��д������ N/A |
| `service` | `vulSvc` | ֱ�� |
| `url` | `vulNetAddr` | �� target ������ url |
| `description` | `vulDesc` | ֱ�� |
| `solution` | `remed` | ֱ�� |
| `sysId` / `sysName` | `objectName` / `assetName` | ���ʲ���ȫ�߼� |
| `targetType` | `isAccess` | normal��0, internet��1��98 ��͸�������� |
| `taskSource` | `source` | own��1(��ҵ����), parent��0 |
| `realTaskId` | `tskSubId` | ���� Batch 1 ������ӳ�� |
| `createTime` | `transferTime`����̬�� | ��ʽ������ʱ��� |
| `updateTime` | `transferTime`����ǰ̬�� | ȡ���� |
| `recordStatus` | �� | ��д�� inst����������� |
| �� | `data_origin` | �̶� `METRIC` |
| �� | `label` | �̶� `1`��ϵͳ©���� |
| �� | `logIDLst` | Ǩ����**����**��oper `ledger_status=PENDING` |

**ָ��ȥ��**������ `vuln_sys.getUniqueKey()` �� pass `getUniqueKey()` ���룻��ͻʱ�� model ���� `updateTime` Ϊ׼�ϲ���

---

## ��¼ B��`vuln_sys_history` �� `rela_oper` �ֶ�ӳ��

> ��ӽű� Batch 3��**ÿ�� history һ�� oper**��`synthesized=0`��

| Դ�ֶ� | `vul_inst_log_rela_oper` | ���� |
|--------|--------------------------|------|
| `id` (history UUID) | `id` | ������ |
| �� `vuln_sys.id` | `vul_info_id` | �� `migration_id_map` ת pass inst id |
| `status` | `vul_info_stat` | ��¼ C |
| `updateTime` | `transfer_time` | ����ʱ�����ʽ |
| `realTaskId` | `tsk_id` | ������ӳ���ת pass ������ id |
| �� | `order_id` | **NULL**�������޲���ָ� |
| �� | `log_ids` | **NULL** |
| �� | `ledger_status` | `PENDING` |
| �� | `data_origin` | `METRIC` |
| �� | `synthesized` | `0` |
| `taskSource` | `source` | ͬ��¼ A |
| �� | `src_method` | Ĭ����ҵ���ֶ�Ӧ�� |
| �� | `eng_hash` | NULL ��������Ĭ��ֵ |

**�� history ��ʵ��**���� `vuln_sys` ��ǰ�кϳ� **1 ��** oper��`transfer_time=updateTime`����

**����**��ͬһ `vul_info_id` �� `transfer_time` ������룬����������Ӫ�켣��

---

## ��¼ C��״̬��ӳ�䣨`VulnStatusEnum` �� `VulStateEnum`��

> model ʹ���ַ����룻pass ʹ�����������롣��ӽű����˹����˹��ñ�����

| model `status` | model ���� | pass `vulInfoStat` | pass ���� | ��ע |
|----------------|------------|-------------------|-----------|------|
| `0` | Ǳ��Ԥ�� | `0` | Ǳ��Ԥ�� | ֱӳ |
| `1` | ��ʼ���� | `1` | ��ʼ���� | ֱӳ |
| `2` | �˹����� | `2` | ����֤��Ч | **����Ʒȷ��**������Ϊ `1` |
| `3` | ����֤��Ч | `2` | ����֤��Ч | model/pass ��ֵ��ͬ |
| `4` | ����֤�� | `3` | ����֤�� | model `4` �� pass `3` |
| `5` | ����֤���� | `3` | ����֤�� | **����Ʒȷ��**����ӳ�� |
| `6` | ���޸� | `5` | ���޸� | model `6` �� pass `5` |
| `7` | �����޸� | `6` | �����޸� | model `7` �� pass `6` |
| `8` | ����δ�޸� | `7` | ����δ�޸� | model `8` �� pass `7` |
| `10` | �˹����� | `1` | ��ʼ���� | ���� |
| `99` / ���� | NONE | �� | �� | ������챨�棬�˹����� |

**ԾǨ����**��Ǩ��**������ִ��** `transition`���� history ��ʵ״̬Ϊ׼д�� oper��inst ȡ����һ�� oper �� `vul_info_stat`��

---

## ��¼ D����Ӷ���ָ��

| # | ָ�� | ��ֵ |
|---|------|------|
| 1 | `vuln_sys` ���� = `vul_archive_inst`��data_origin=METRIC������ | 100% |
| 2 | ÿ�� inst ���� 1 �� oper | 100% |
| 3 | `vuln_sys_history` ���� = oper �������� history ��ʵ���� | ��0 |
| 4 | ״̬ӳ��ʧ���� | 0������� CSV �˹��ջ��� |
| 5 | ����������ѣ�tsk_id �޷������� | <0.1% |
| 6 | �ʲ��޷�ӳ���� | ���뱨�棬����ϸ�� |
| 7 | ָ�Ƴ�ͻ�ϲ��� | ���뱨�� |

**dry-run ������**��`migration_report_{date}.csv`�������� 7 ����ϸ����

---

## ��¼ E���������������д��

| # | ���� | ���� | ���� |
|---|------|------|------|
| 1 | ��ʷȫ��Ǩ oper | **��**����ȷ�ϣ� | ? ��ȷ�� |
| 2 | `status=2` �˹�����ӳ�� | ӳ��Ϊ pass `2` ����֤��Ч | |
| 3 | `status=5` ����֤����ӳ�� | ӳ��Ϊ pass `3` ����֤�� | |
| 4 | pass inst `id` ���ɹ��� | ���� pass ���з��Ų��� | |
| 5 | ��Ӵ���ʱ��Ŀ�� | ���� ��4h���������� dry-run �ⶨ�� | |

---

## ��¼ F����˫�췽�� Wave ����

| ˫�� Wave | ������ Phase | ��ϵ |
|-----------|--------------|------|
| Wave 0 �̵� | Phase 0 | ���� |
| Wave 1 Schema | Phase 1 | **Ӳ����** |
| Wave 2 ��ѯ���� | �� | ���������漰���޾� API �л��� |
| Wave 3 ��ѡ�ϳ� | Phase 2 ĩ / ��Ӻ����� | �ɵ��� |
| Wave 4 ȥ Excel | Phase 4 ��� | �ϲ����� |
