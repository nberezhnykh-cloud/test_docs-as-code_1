function Div(el)
  -- Применяем стили Word по классам
  for _, class in ipairs(el.classes) do
    if class == "warning" then
      el.attributes["custom-style"] = "WarningText"
    elseif class == "note" then
      el.attributes["custom-style"] = "NoteText"
    elseif class == "custom-paragraph" then
      el.attributes["custom-style"] = "CustomParagraph"
    elseif class == "CustomText" then
      el.attributes["custom-style"] = "_text"
    elseif class == "CustomList1" then
      el.attributes["custom-style"] = "_list-1-lvl"
    elseif class == "CustomList2" then
      el.attributes["custom-style"] = "_list-2-lvl"
    elseif class == "CustomList3" then
      el.attributes["custom-style"] = "_list-3-lvl"
    elseif class == "CustomList4" then
      el.attributes["custom-style"] = "_list-4-lvl"
    elseif class == "PictureName" then
      el.attributes["custom-style"] = "_Picture-name"
    elseif class == "Picture" then
      el.attributes["custom-style"] = "_Picture"
    end
  end

  -- Обработка подписей изображений
  if el.classes:includes("imageblock") then
    local new_content = {}
    for _, block in ipairs(el.content) do
      if block.t == "Div" and block.classes:includes("title") then
        local caption_text = pandoc.utils.stringify(block.content)
        local new_caption = caption_text:gsub("^Figure (%d+)%.%s+", "Рисунок %1 – ")
        if new_caption ~= caption_text then
          local new_block = pandoc.Div({ pandoc.Plain(pandoc.Str(new_caption)) }, block.attr)
          table.insert(new_content, new_block)
        else
          table.insert(new_content, block)
        end
      else
        table.insert(new_content, block)
      end
    end
    el.content = new_content
    return el
  end

  return el
end

function Table(el)
  -- Обработка подписей таблиц
  if el.caption and el.caption.long then
    local caption_text = pandoc.utils.stringify(el.caption.long)
    local new_caption_text = caption_text:gsub("^Table (%d+)%.%s+", "Таблица %1 – ")
    if new_caption_text ~= caption_text then
      local styled_caption = pandoc.Span({ pandoc.Str(new_caption_text) }, {["custom-style"] = "_Table-caption"})
      el.caption.long = { styled_caption }
    end
  end
  return el
end

function Span(el)
  for _, class in ipairs(el.classes) do
    if class == "highlight" then
      el.attributes["custom-style"] = "HighlightInline"
    end
  end
  return el
end