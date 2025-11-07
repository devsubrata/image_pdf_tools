from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    A FileField that accepts multiple files (a list of InMemoryUploadedFile objects).
    """

    widget = MultipleFileInput

    def to_python(self, data):
        # data is normally a list from request.FILES.getlist(...)
        if not data:
            return []
        # If a single file is passed, wrap it in a list
        if not isinstance(data, (list, tuple)):
            return [data]
        return list(data)

    def validate(self, data):
        # `data` is a list here
        if not data:
            raise forms.ValidationError("No files uploaded.")
        # Validate each file using parent FileField logic
        for f in data:
            super().validate(f)


class ExtractPagesForm(forms.Form):
    pdf_file = forms.FileField(label="Upload PDF")
    page_range = forms.CharField(
        label="Pages to extract (e.g., 1-3,5,8)",
        required=False,  # Optional, since user may choose odd/even/all instead
        help_text="Use commas and hyphens to specify page ranges. Leave blank to extract odd, even, or all pages."
    )
    page_type = forms.ChoiceField(
        label="Page Selection Type",
        choices=[
            ('all', 'All Pages'),
            ('odd', 'Odd Pages Only'),
            ('even', 'Even Pages Only'),
        ],
        initial='all',
        help_text="Ignored if specific page ranges are provided above."
    )


class CombinePdfsForm(forms.Form):
    pdf_files = MultipleFileField(
        label="Upload PDFs",
        widget=MultipleFileInput(attrs={'multiple': True})
    )
    add_bookmarks = forms.BooleanField(
        label="Add bookmarks from filenames?",
        required=False
    )
