package fr.jsisie.urbinema.ui.theme

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.KeyboardArrowDown
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import fr.jsisie.urbinema.R

@Composable
fun ThemePickerButton(
    selected: UrbinemaThemeMode,
    onOpen: () -> Unit,
    modifier: Modifier = Modifier,
) {
    OutlinedButton(
        onClick = onOpen,
        modifier = modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
        ) {
            ThemeSwatches(selected)
            Text(
                stringResource(selected.labelRes),
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.titleMedium,
            )
            Icon(Icons.Outlined.KeyboardArrowDown, contentDescription = null)
        }
    }
}

@Composable
fun ThemePickerDialog(
    selected: UrbinemaThemeMode,
    onSelect: (UrbinemaThemeMode) -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.theme)) },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 420.dp)
                    .verticalScroll(rememberScrollState()),
            ) {
                UrbinemaThemeMode.entries.forEach { mode ->
                    ThemeOptionRow(
                        mode = mode,
                        selected = mode == selected,
                        onSelect = { onSelect(mode) },
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.theme_close))
            }
        },
    )
}

@Composable
private fun ThemeOptionRow(
    mode: UrbinemaThemeMode,
    selected: Boolean,
    onSelect: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(role = Role.RadioButton, onClick = onSelect)
            .padding(vertical = UrbinemaThemeTokens.dimens.xs),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        RadioButton(selected = selected, onClick = null)
        Text(
            stringResource(mode.labelRes),
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodyLarge,
        )
        ThemeSwatches(mode)
    }
}

@Composable
private fun ThemeSwatches(mode: UrbinemaThemeMode) {
    val swatches = paletteFor(mode, isSystemInDarkTheme()).previewSwatches()
    val ring = UrbinemaThemeTokens.colors.outline
    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
        swatches.forEach { color ->
            Box(
                modifier = Modifier
                    .size(18.dp)
                    .clip(CircleShape)
                    .background(color)
                    .border(1.dp, ring, CircleShape),
            )
        }
    }
}
