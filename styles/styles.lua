-- mapping block roles → Word styles
function Div(el)
  for _, class in ipairs(el.classes) do
    if class == "warning" then
      el.attributes["custom-style"] = "WarningText"
    elseif class == "note" then
      el.attributes["custom-style"] = "NoteText"
    elseif class == "custom-paragraph" then
      el.attributes["custom-style"] = "CustomParagraph"
    end
  end
  return el
end

-- mapping inline roles → Word styles
function Span(el)
  for _, class in ipairs(el.classes) do
    if class == "highlight" then
      el.attributes["custom-style"] = "HighlightInline"
    end
  end
  return el
end