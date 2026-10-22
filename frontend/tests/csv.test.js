import test from 'node:test'
import assert from 'node:assert/strict'
import {
  parseCsvLine,
  parseCsvText,
  parseAndValidateCsv,
} from '../src/composables/useImportExport.js'

test('parseCsvLine parses simple comma separated values', () => {
  const line = '张三,技术部,zhangsan@example.com'
  const fields = parseCsvLine(line)
  assert.deepEqual(fields, ['张三', '技术部', 'zhangsan@example.com'])
})

test('parseCsvLine preserves commas inside quotes according to RFC 4180', () => {
  const line = '李四,"北京市, 朝阳区, 望京","13800138000"'
  const fields = parseCsvLine(line)
  assert.deepEqual(fields, ['李四', '北京市, 朝阳区, 望京', '13800138000'])
})

test('parseCsvLine correctly handles escaped double quotes', () => {
  const line = '王五,"他说：""你好，世界""","13900139000"'
  const fields = parseCsvLine(line)
  assert.deepEqual(fields, ['王五', '他说："你好，世界"', '13900139000'])
})

test('parseAndValidateCsv classifies valid and invalid rows with reasons', () => {
  const csvContent = [
    '姓名,部门,邮箱,手机号码',
    '张伟,技术研发部,zhangwei@example.com,13800138001',
    '李四,非法部门,invalid-email,123',
  ].join('\r\n')

  const schema = [
    { key: 'name', title: '姓名', validator: (v) => (!v ? '姓名必填' : null) },
    {
      key: 'department',
      title: '部门',
      validator: (v) => (v !== '技术研发部' ? '部门无效' : null),
    },
    {
      key: 'email',
      title: '邮箱',
      validator: (v) => (!v || !v.includes('@') ? '邮箱不合法' : null),
    },
    {
      key: 'phone',
      title: '手机号码',
      validator: (v) => (!/^\d{11}$/.test(v) ? '手机须为11位' : null),
    },
  ]

  const result = parseAndValidateCsv(csvContent, schema)
  assert.equal(result.validRows.length, 1)
  assert.equal(result.failedRows.length, 1)
  assert.equal(result.validRows[0].name, '张伟')
  assert.equal(result.failedRows[0].rowNum, 3)
  assert.equal(result.failedRows[0].errors.length, 3)
})
