/**
 * useImportExport - 统一的 CSV 解析、校验与导出复用逻辑 (遵循 RFC 4180 标准)
 */

/**
 * 符合 RFC 4180 标准的单行 CSV 解析状态机
 * 正确处理带逗号、转义双引号（""）以及首尾空格的字段
 * @param {string} line 单行文本
 * @returns {string[]} 解析出的字段数组
 */
export function parseCsvLine(line) {
  const fields = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < line.length; i++) {
    const char = line[i]

    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        // 双引号转义："" -> "
        current += '"'
        i++
      } else {
        // 进入或退出引号区域
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      // 字段结束
      fields.push(current.trim())
      current = ''
    } else {
      current += char
    }
  }

  fields.push(current.trim())
  return fields
}

/**
 * 解析多行 CSV 文本（正确兼容包含换行及空行的文本）
 * @param {string} text CSV 纯文本
 * @returns {string[][]} 解析出的二维矩阵
 */
export function parseCsvText(text) {
  const rows = []
  let currentRow = []
  let currentField = ''
  let inQuotes = false

  for (let i = 0; i < text.length; i++) {
    const char = text[i]

    if (char === '"') {
      if (inQuotes && text[i + 1] === '"') {
        currentField += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      currentRow.push(currentField.trim())
      currentField = ''
    } else if ((char === '\r' || char === '\n') && !inQuotes) {
      if (char === '\r' && text[i + 1] === '\n') {
        i++
      }
      currentRow.push(currentField.trim())
      // 忽略空行
      if (currentRow.some((f) => f.length > 0)) {
        rows.push(currentRow)
      }
      currentRow = []
      currentField = ''
    } else {
      currentField += char
    }
  }

  if (currentField.length > 0 || currentRow.length > 0) {
    currentRow.push(currentField.trim())
    if (currentRow.some((f) => f.length > 0)) {
      rows.push(currentRow)
    }
  }

  return rows
}

/**
 * 将数据数组安全格式化并导出为 CSV 文件
 * 严格转义包含逗号、引号与换行符的内容
 * @param {Array<Object>} data 导出的数据对象数组
 * @param {Array<{ key: string, title: string }>} columns 列映射配置
 * @param {string} filename 下载的文件名（无需后缀）
 */
export function exportToCsv(data, columns, filename = 'export') {
  if (!data || !data.length) {
    throw new Error('没有可导出的数据')
  }

  const formatValue = (val) => {
    if (val === null || val === undefined) return '""'
    const str = String(val)
    return `"${str.replace(/"/g, '""')}"`
  }

  const headers = columns.map((col) => formatValue(col.title || col.key))
  const rows = data.map((item) => columns.map((col) => formatValue(item[col.key])).join(','))

  const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\r\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}_${Date.now()}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 解析并校验导入的 CSV 文本数据
 * @param {string} text CSV 纯文本
 * @param {Array<{ key: string, title: string, validator?: (val, row) => string | null }>} schema 列校验规则
 * @returns {{ validRows: Array<Object>, failedRows: Array<{ rowNum: number, errors: string[], raw: Object }> }}
 */
export function parseAndValidateCsv(text, schema) {
  const rows = parseCsvText(text)
  if (rows.length < 2) {
    throw new Error('导入文件至少需包含表头和一条有效数据')
  }

  const rawHeaders = rows[0]
  const headerMap = {}
  schema.forEach((col) => {
    const idx = rawHeaders.findIndex((h) => h === col.title || h === col.key)
    if (idx !== -1) {
      headerMap[col.key] = idx
    }
  })

  const validRows = []
  const failedRows = []

  for (let i = 1; i < rows.length; i++) {
    const rowValues = rows[i]
    const rowNum = i + 1
    const rowData = {}
    const errors = []

    schema.forEach((col) => {
      const colIdx = headerMap[col.key]
      const val = colIdx !== undefined ? rowValues[colIdx] : undefined
      rowData[col.key] = val || ''

      if (col.validator) {
        const errMsg = col.validator(val, rowData)
        if (errMsg) {
          errors.push(`[${col.title}]: ${errMsg}`)
        }
      }
    })

    if (errors.length > 0) {
      failedRows.push({ rowNum, errors, raw: rowData })
    } else {
      validRows.push(rowData)
    }
  }

  return { validRows, failedRows }
}
